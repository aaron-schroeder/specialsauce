import math
import time

import pandas as pd

from specialsauce.sources.strava import gap_speed, gap_speed_np, gap_speed_pickle
from specialsauce.speed_adjustment import gap_speed as gap_speed_sa

SPEED = 'speed'
GRADE = 'grade'

n_t = 60 * 60 * 3  # 3 hours in seconds
times = range(n_t)
df = pd.DataFrame.from_dict({
  'time': times,
  GRADE: [-4 * math.sin(0.01 * t) for t in times],
  SPEED: [3.0 + math.sin(0.1 * t) for t in times],
})

t1 = time.time()
r1 = [gap_speed_np(s, g / 100) for s, g in zip(df[SPEED], df[GRADE])]
t2 = time.time()
r2 = [gap_speed(s, g / 100) for s, g in zip(df[SPEED], df[GRADE])]
t3 = time.time()
r3 = [gap_speed_sa(s, g / 100) for s, g in zip(df[SPEED], df[GRADE])]
t4 = time.time()
r4 = [gap_speed_pickle(s, g / 100) for s, g in zip(df[SPEED], df[GRADE])]
t5 = time.time()

# t1 = time.time()
# r1 = [gap_factor(g / 100) for g in grades]
# t2 = time.time()
# r2 = [gap_factor_interp(g / 100) for g in grades]
# t3 = time.time()
# r3 = [gap_factor(g / 100) for g in grades]
# t4 = time.time()

print(f'Polynomial: {t2 - t1} sec')
print(f'Interp: {t3 - t2} sec')
print(f'Interp from file: {t4 - t3} sec')
print(f'Pickle: {t5 - t4} sec')
