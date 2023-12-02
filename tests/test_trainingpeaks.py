import unittest

from specialsauce.sources.trainingpeaks import ewma_days, sma


class TestEwmaDays(unittest.TestCase):
  def test_stable(self):
    init = 100.0
    result = ewma_days(
      [init if i != 0 else 0 for i in range(5)],
      7,
      init=init
    )
    for el in result:
      self.assertAlmostEqual(el, init)


class TestSma(unittest.TestCase):
  def test_sma(self):
    # x = pd.Series([10 for i in range(60)])
    # x.rolling(30).mean()  # nan until 29

    # x.index = [pd.to_datetime(2*i, unit='s') for i in range(len(x))]
    # x = pd.Series([i for i in range(60)])
    # x.index = [pd.to_datetime(2*i, unit='s') for i in range(len(x))]
    # x.rolling('30s').mean()

    pass