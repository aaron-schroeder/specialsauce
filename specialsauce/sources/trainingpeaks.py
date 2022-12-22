import numpy as np
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