import unittest

from specialsauce.sources.minetti import cost_of_running, cost_of_walking


class FactorTestMixin:
  func = None
  range_min = None
  range_max = None

  @classmethod
  def setUpClass(cls):
    cls.func = staticmethod(cls.func)

  def test_below_range(self):
    self.assertEqual(
      self.func(self.range_min),
      self.func(self.range_min - 0.01)
    )

  def test_above_range(self):
    self.assertEqual(
      self.func(self.range_max),
      self.func(self.range_max + 0.01)
    )


class TestMinettiRun(FactorTestMixin, unittest.TestCase):
  func = cost_of_running
  range_min = -0.45
  range_max = 0.45


class TestMinettiWalk(FactorTestMixin, unittest.TestCase):
  func = cost_of_walking
  range_min = -0.45
  range_max = 0.45
