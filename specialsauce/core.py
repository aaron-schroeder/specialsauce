import math

import numpy as np
import pandas as pd

from specialsauce import util
from specialsauce.sources import minetti


def power_met_ss(speed, grade=0.0):
  return speed * minetti.cost_of_running(grade)


def power_met_ss(speed_series, grade_series=None):
  """Calculate steady-state metabolic power in the moderate domain.

  For more info, see `heartandsole_local/heartandsole/powerutils.py`.
  """
  if grade_series is None:
    grade_series = pd.Series([0 for i in range(len(speed_series))])

  c_i_series = grade_series.apply(minetti.cost_of_running)

  # Instantaneous running power (W/kg) is simply cost of running 
  # (J/kg/m) multiplied by speed (m/s).
  power_series = c_i_series * speed_series
  
  # Updated to account for the fact that the horizontal speed is
  # measured, but cost of running relates to the distance along the
  # incline.
  power_series = power_series / np.cos(np.arctan(grade_series))

  return power_series


def power_met(speed_series, grade_series=None, time_series=None, tau=20):
  """Calculate metabolic power in the moderate domain as a time series."""
  if time_series is None:
    time_series = pd.Series([i for i in range(len(speed_series))])

  # Calculate the theoretical steady-state power associated with the
  # speed and grade value at each timestep.
  power_met_inst = power_met_ss(speed_series, grade_series=grade_series)

  halflife = tau * math.log(2)

  # Even if we have uniform 1-second samples, I would still need this
  # util function. It makes the average start at 0 and trend up, rather
  # than letting the first value have all the weight.

  return util.ewma_halflife(
    power_met_inst,
    halflife,
    time_series=time_series,
  )


def run_cost(grade=0.0):
  """Calculates the metabolic cost of running.

  See the documentation for powerutils.o2_power_ss for information
  on the scientific basis for this calculation.

  Args:
    speed (float): Running speed in meters per second. 
    grade (float): Decimal grade, i.e. 45% = 0.45.

  Returns:
    float: Cost of running on an inclined treadmill, in Joules/kg/m,
      with distance measured along the incline slope.
  """
  c_i = minetti.cost_of_running(grade)

  return c_i


def run_power(speed, grade=0.0):
  return run_cost(speed, grade=grade) * speed / math.cos(math.atan(grade))
