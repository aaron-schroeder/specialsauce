import numpy as np
from numpy.polynomial import Polynomial
import pickle
from scipy.interpolate import interp1d


def gap_speed_factor(decimal_grade):
  """Calculate Strava's GAP speed-factor as a function of percent grade.

  The factor will be greater than 1.0 if GAP is faster than horizontal speed,
  and less than 1.0 if GAP is slower than horizontal speed.

  This function is the result of an experiment I performed with Strava.
  I spoofed activity files to upload to Strava to reverse-engineer
  their formula for Grade Adjusted Pace (GAP). The files each depicted a
  runner moving at a constant speed up a constant incline. I then took a ratio
  of the grade-adjusted speeds to horizontal speeds at a variety of speed and 
  grade combinations.

  I found that Strava applies a pace adjustment factor that is dependent only
  on grade (ie independent of speed).

  Grade is constrained to (-45%, 45%), because that was the range of grades
  in my investigation. That range also coincides with the values investigated
  by Minetti (2002). Rather than extrapolating outside of that range, I chose
  to cap the adjustment factor.
  
  Strava's GAP is now a HR-based, big data-derived quantity, so I don't know
  how reasonable it is at the steepest grades; there are certainly fewer data
  points to go on at the extreme ends of the range. In other analyses I've
  done, I don't think I have seen Strava report a grade steeper than 50%, 
  so it is possible that defines its range of the GAP formula's validity. 
  Strava seems to smooth its elevation and/or grade time series to fit into
  this range.

  Args:
    grade (float): Decimal grade to evaluate the GAP speed-factor.
  Returns:
    float: Factor that converts speed to grade-adjusted speed.
  """
  # Constrain decimal grade to the range of the equation's validity
  decimal_grade = np.clip(decimal_grade, -0.45, 0.45)

  adjustment_factors = {
    45: 4.286,
    30: 3.158,
    25: 2.727,
    20: 2.297,
    15: 1.846,
    10: 1.459,
    8: 1.337,
    6: 1.228,
    4: 1.135,
    2: 1.055,
    0: 1.0,
    -2: 0.96,
    -4: 0.918,
    -6: 0.891,
    -8: 0.876,
    -10: 0.876,
    -15: 0.941,
    -20: 1.081,
    -25: 1.273,
    -30: 1.495,
    -45: 2.096
  }

  interp_fn = interp1d(
    list(adjustment_factors.keys()),
    list(adjustment_factors.values())
  )

  return interp_fn(decimal_grade * 100)


def gap_speed_factor_np(decimal_grade):
  g_percent = decimal_grade * 100
  
  g_min = -45
  g_max = 45

  factor_fn = Polynomial(
    [0.99743571, 1.35615613, 3.69628995, -0.15317883, -1.50476068, -0.10920085],
    domain=[g_min, g_max],
  )

  factor_min = factor_fn(g_min)
  factor_max = factor_fn(g_max)

  return np.piecewise(
    g_percent,
    [g_percent < g_min, (g_percent >= g_min) & (g_percent <= g_max), g_percent > g_max],
    [lambda g: factor_min, lambda g: factor_fn(g), lambda g: factor_max]
  )


def gap_speed_factor_pickle(grade):
  with open('gap_interp', 'rb') as f:
    fnc = pickle.load(f)
  return fnc(grade)


def gap_speed(speed, grade):
  return speed * gap_speed_factor(grade)


def gap_speed_np(speed, grade):
  return speed * gap_speed_factor_np(grade)


def gap_speed_pickle(speed, grade):
  return speed * gap_speed_factor_pickle(grade)