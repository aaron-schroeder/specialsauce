import math

import numpy as np

from fitanalysis.activity import Activity
import fitanalysis.spatialutils as su
import fitanalysis.powerutils as pu


def moving_average(a, n=30) :
  ret = np.cumsum(a, dtype=float)
  ret[n:] = ret[n:] - ret[:-n]
  return ret[n - 1:] / n


if __name__ == '__main__':
  # User input.
  file_dir = './activity_files/'
  pace_min_mile = 8
  grade = 0.00  # decimal grade
  duration = 60.0  # mins

  # Calculate metrics with fitanalysis methods for comparison.
  activity = Activity(file_dir+'3981100861.fit')

  n_t = duration * 60 + 1
  speed_ms = 1609.34 / (pace_min_mile * 60)
  speeds_ms = [speed_ms for _ in range(n_t)]
  grades = [grade for _ in range(n_t)]

  c_rs = pu.run_cost(speeds_ms, grades)
  #c_r_smooth = fitanalysis.util.moving_average(c_r, 120)

  #run_power = c_r*speed_ms
  #run_power = [c_r * speed_ms for c_r, speed_ms in zip(c_rs, speeds_ms)]
  run_power = pu.run_power(speeds_ms, grades)
  #run_power = fitanalysis.util.moving_average(c_r * speeds_ms, 30)
  #run_power = fitanalysis.util.moving_average(c_r_smooth * self.data['speed'], 30)

  #run_power = 
  avg_power = np.mean(run_power)
  norm_power = np.sqrt(np.sqrt(
                np.mean(moving_average(run_power) ** 4)))

  IF = norm_power/pu.flat_run_power('6:30')
  print('IF = %0.2f' % IF)
  govss = duration * IF**2 * 100.0/60.0 
  print('GOVSS = %d' % govss)
  scaled_pace = 6.5/IF
  print('Scaled pace = %d:%02d' % 
      (math.floor(scaled_pace), 60*(scaled_pace-math.floor(scaled_pace))))
  y = norm_power
  value = (25*y**2 + 8640)**0.5 + 5*y
  speed_equiv = (5**(1/3)*(value)**(2/3) - 12*5**(2/3))/(value**(1/3))
  pace_equiv = 1609.34/(60.0*speed_equiv)
  print('Equivalent-power pace = %d:%02d' %
      (math.floor(pace_equiv), 60*(pace_equiv-math.floor(pace_equiv))))
  print('Elevation gain = %d ft' % 
      (sum([speed*grade*5280/1609.34 for speed in speeds_ms]),)) 
  print('Calories burned = %d' % (avg_power*duration*75.0*60.0/4186))