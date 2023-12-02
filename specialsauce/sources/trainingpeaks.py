import numpy as np
import pandas as pd
from scipy.interpolate import interp1d


def ngp_speed_factor(decimal_grade):
  """Calculate TrainingPeaks' NGP pace-factor as a function of percent grade.

  The factor will be greater than 1.0 if NGP is faster than horizontal speed,
  and less than 1.0 if NGP is slower than horizontal speed.

  Grade is constrained to (-25%, 30%), because that was the range of grades
  that yielded reasonable paces in my investigation:
    * 0.45 adjusted 8:00 pace to 0:17 pace.
    * The adjustment factor jumped wildly from -26% to -27% and from
      31% to 32%.

  Rather than extrapolating outside of that range, I chose to cap the 
  adjustment factor.

  TrainingPeaks does not provide any info about how they derived their
  grade adjustment factor, but the shape of the curve sure looks a lot
  like Strava's GAP.

  Args:
    grade (float): Decimal grade to evaluate the NGP speed-factor.
  Returns:
    float: Factor that converts speed to NGP adjusted speed.
  """
  # Constrain decimal grade to the range of the equation's validity
  decimal_grade = np.clip(decimal_grade, -0.25, 0.3)

  adjustment_factors = {
    45: 28.235,
    32: 20.0,
    31: 3.556,
    30: 3.429,
    25: 2.874,
    20: 2.365,
    15: 1.905,
    10: 1.514,
    8: 1.383,
    6: 1.266,
    4: 1.162,
    2: 1.074,
    0: 1.0,
    -2: 0.941,
    -4: 0.897,
    -6: 0.87,
    -8: 0.856,
    -10: 0.857,
    -15: 0.921,
    -20: 1.067,
    -25: 1.28,
    -26: 1.33,
    -27: 2.051,
    -30: 2.297,
    -45: 3.934
  }

  interp_fn = interp1d(
    list(adjustment_factors.keys()),
    list(adjustment_factors.values())
  )

  return interp_fn(decimal_grade * 100)


def normalize(series):
  """Calculates the TrainingPeaks norm of a series of data.

  This works like a modified version of an average, based on principles
  of human physiology.

  First, a 30-second rolling average is applied to the series. 
  Since this norm is meant to replicate TrainingPeaks NP/NGP, I follow
  their lead in throwing out the first `window_len` of data 
  (30 sec in their case).

  Note: I'm not sure if this means they insert 0 values for the first
  30 seconds, or if they take an average of points after 30 seconds.
  My EWMA function (below) slowly increments until it gets to a
  steady-state - so it is biased to be low for short-duration bouts.

  Then, the L4 norm is applied to the smoothed series. This norm 
  emphasizes higher values by raising all values to the 4th power, 
  averaging them, then taking the 4th root.
  
  Emphasizing higher values is based in the idea that best-fit curves 
  between VO2 (oxygen consumption) and blood lactate tend to follow a 
  4th-order relationship.

  References:
    https://help.trainingpeaks.com/hc/en-us/articles/204071804-Normalized-Power

  """
  series_rolling = sma(series, 30)
  return l4_norm(series_rolling[29:])


def sma(x_series, window_len, time_series=None):
  """Simple moving average, as implemented by TrainingPeaks."""

  if time_series is None:
    sma = x_series.rolling(window_len).mean()
  else:
    # Assume we are working with seconds.
    if isinstance(window_len, (int, float)):
      window_len = pd.to_timedelta(window_len, unit='s')
    elif isinstance(window_len, str):
      window_len = pd.to_timedelta(window_len)

    x_series.index = time_series.map(lambda x: pd.to_datetime(x, unit='s'))

    sma = x_series.rolling(window_len).mean()

    sma.index = time_series.index

  return sma


def l4_norm(series):
  return (series ** 4).mean() ** 0.25


def training_stress_score(ngp, ftp, duration_sec):
  """TSS"""
  return 100 * (ngp / ftp) ** 2 * (duration_sec / 3600)


def acute_training_load(tss_array, init=0.0):
  """ATL

  Args:
    tss_arr (list-like): array of Training Stress Score values, assumed
      to occur exactly [0, 1, 2, ...] days from now.
  """
  return ewma_days(tss_array, 7, init)


def chronic_training_load(tss_array, init=0.0):
  """CTL

  Args:
    tss_arr (list-like): array of Training Stress Score values, assumed
      to occur exactly [0, 1, 2, ...] days from now.
  """
  return ewma_days(tss_array, 42, init)


def ewma_days(x_array, n_days, init=0.0):
  alpha = 1 / n_days
  
  return [
    init * (1 - alpha) ** i + sum(
      x_array[i - n] * alpha * (1 - alpha) ** n 
      for n in range(i + 1)) 
    for i in range(len(x_array))
  ]


def training_status(training_stress_balance):
  if training_stress_balance > 25:
    return 'Likely losing fitness quickly'
  elif training_stress_balance > 15:
    return 'Extensively recovered and likely losing fitness'
  elif training_stress_balance > -10:
    return 'Maintenance'
  elif training_stress_balance > -30:
    return 'Productive'
  else:
    return 'Overreaching'
