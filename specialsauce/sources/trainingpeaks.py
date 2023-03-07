import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from specialsauce import util


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


def sma(x_series, window_len, time_series=None):
  """Simple moving average.
  
  Since this is used to replicate TrainingPeaks NP/NGP, I throw out the
  first `window_len` of data (30 sec in their case).
  https://help.trainingpeaks.com/hc/en-us/articles/204071804-Normalized-Power

  I'm really not sure if this means they insert 0 values for the first
  30 seconds, or if they take an average of points after 30 seconds.
  My EWMA function (below) slowly increments until it gets to a
  steady-state - so it is biased to be low for short-duration bouts.
  """

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


def lactate_norm(series):
  """Calculates lactate norm of a series of data.

  Unlike a simple average, the lactate norm emphasizes higher values
  by raising all values to the 4th power, averaging them, then taking
  the 4th root. Emphasizing higher values is rooted in the fact that
  best-fit curves between VO2 (oxygen consumption) and lactate tend
  to follow a 4th-order relationship.

  """
  return (series ** 4).mean() ** 0.25


def ngp_speed(speed, grade):
  return speed * ngp_speed_factor(grade)


def ewma_days(x_arr, n_days, init=0.0):
  alpha = 1 / n_days
  
  return [
    init * (1 - alpha) ** i + sum(
      x_arr[i-n] * alpha * (1 - alpha) ** n 
      for n in range(i+1)) 
    for i in range(len(x_arr))
  ]


def acute_training_load(tss_arr, init=0.0):
  """
  Args:
    tss_arr (list-like): array of Training Stress Score values, assumed
      to occur exactly [0, 1, 2, ...] days from now.
  """
  return ewma_days(tss_arr, 7, init)


def chronic_training_load(tss_arr, init=0.0):
  """
  Args:
    tss_arr (list-like): array of Training Stress Score values, assumed
      to occur exactly [0, 1, 2, ...] days from now.
  """
  return ewma_days(tss_arr, 42, init)


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


def training_stress_score(ngp, ftp, duration_sec):
  """TSS"""
  return 100 * (ngp / ftp) ** 2 * (duration_sec / 3600)


def ngp_val(ngp_array):
  ngp_rolling = sma(ngp_array, 30)
  return lactate_norm(ngp_rolling[29:])


def chronic_training_load(stress_arr, day_arr):
  """CTL
  
  Args:
    stress_arr (list(float)): Training stresses from a series of workouts.
    day_arr (list(datetime.timedelta, datetime.datetime, or datetime.date)):
      The time when each workout was performed. 
  """
  return util.ewma(stress_arr, day_arr, 1/42)


def acute_training_load(stress_arr, day_arr):
  """ATL
  
  Args:
    stress_arr (list(float)): Training stresses from a series of workouts.
    day_arr (list(datetime.timedelta, datetime.datetime, or datetime.date)):
      The time when each workout was performed. 
  """
  return util.ewma(stress_arr, day_arr, 1/7)


def training_stress_balance(stress_arr, day_arr):
  """TSB
  
  Args:
    stress_arr (list(float)): Training stresses from a series of workouts.
    day_arr (list(datetime.timedelta, datetime.datetime, or datetime.date)):
      The time when each workout was performed. 
  """
  return acute_training_load(stress_arr, day_arr)  \
       - chronic_training_load(stress_arr, day_arr)


def calc_ctl_atl(df):
  """Add power-related columns to the DataFrame.
  
  From my `distilling-flask` project.

  For more, see boulderhikes.views.ActivityListView

  """
  # atl_pre = [0.0]
  atl_0 = 0.0
  atl_pre = [atl_0]
  atl_post = [ df['tss'].iloc[0] / 7.0 + atl_0]
  
  # ctl_pre = [0.0]
  ctl_0 = 0.0
  ctl_pre = [ctl_0]
  ctl_post = [ df['tss'].iloc[0] / 42.0 + ctl_0]
  for i in range(1, len(df)):
    delta_t_days = (
      df['recorded'].iloc[i] - df['recorded'].iloc[i-1]
    ).total_seconds() / (3600 * 24)
    
    atl_pre.append(
      (atl_pre[i-1] + df['tss'].iloc[i-1] / 7.0) * (6.0 / 7.0) ** delta_t_days
    )
    atl_post.append(
      df['tss'].iloc[i] / 7.0 + atl_post[i-1] * (6.0 / 7.0)  ** delta_t_days
    )
    ctl_pre.append(
      (ctl_pre[i-1] + df['tss'].iloc[i-1] / 42.0) * (41.0 / 42.0) ** delta_t_days
    )
    ctl_post.append(
      df['tss'].iloc[i] / 42.0 + ctl_post[i-1] * (41.0 / 42.0) ** delta_t_days
    )

  df['ATL_pre'] = atl_pre
  df['CTL_pre'] = ctl_pre
  df['ATL_post'] = atl_post
  df['CTL_post'] = ctl_post