import unittest

from specialsauce.sources.minetti import cost_of_running, cost_of_walking
from specialsauce.sources.strava import gap_speed_factor
from specialsauce.sources.trainingpeaks import ngp_speed_factor


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

  def test_percent_grade_input(self):
    self.assertEqual(
      self.func(self.range_max),
      self.func(self.range_max * 100)
    )

    self.assertEqual(
      self.func(self.range_min),
      self.func(self.range_min * 100)
    )


class TestMinettiRun(FactorTestMixin, unittest.TestCase):
  func = cost_of_running
  range_min = -0.45
  range_max = 0.45


class TestMinettiWalk(FactorTestMixin, unittest.TestCase):
  func = cost_of_walking
  range_min = -0.45
  range_max = 0.45


class TestNgp(FactorTestMixin, unittest.TestCase):
  func = ngp_speed_factor
  range_min = -0.25
  range_max = 0.30


class TestGap(FactorTestMixin, unittest.TestCase):
  func = gap_speed_factor
  range_min = -0.45
  range_max = 0.45
