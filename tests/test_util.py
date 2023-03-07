import unittest

import datetime
import math
import os

import numpy as np
import pandas as pd

import specialsauce
from specialsauce import util as putil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


@unittest.skip('I do not have the moving average funcs cleaned up yet')
class TestMovingAverage(unittest.TestCase):
  def test_ewma(self):
    n = 180
    s = pd.Series([10.0 for i in range(n)])
    # s.iloc[2:5] = [np.nan] * 3
    
    tau = 100
    t = pd.Series([t for t in range(len(s))])
    s_theory = 10.0 * (1 - np.exp(-(t+1) / tau))

    halflife = math.log(2) * tau
    
    # print(ewma(s, halflife))
    self.assertAlmostEqual(
      (putil.ewma(s, halflife) - s_theory).max(),
      0
    )

    # print(putil.ewma(s, f'{halflife}s', time_series=t))
    # print(ewma(s, halflife, time_series=t))
    # print(ewma(s, f'{halflife}s', time_series=t) - s_theory)
    self.assertAlmostEqual(
      (putil.ewma(s, f'{halflife}s', time_series=t) - s_theory).max(),
      0
    )

    times = pd.Series([30 + 2 * t for t in range(len(s))])
    s_theory = pd.Series([10.0 * (1 - np.exp(-(2 * t + 1) / tau)) for t in range(len(times))])
    # print(putil.ewma(s, f'{halflife}s', time_series=times))
    self.assertAlmostEqual(
      (putil.ewma(s, f'{halflife}s', time_series=times) - s_theory).max(),
      0
    )

