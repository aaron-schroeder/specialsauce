import unittest

from specialsauce.sources.minetti import cost_of_running, cost_of_walking


class FactorTest:
  pass

class TestMinettiRun(unittest.TestCase):
  def test_below_range(self):
    self.assertEqual(
      cost_of_running(-0.5),
      cost_of_running(-0.45)
    )

  def test_above_range(self):
    self.assertEqual(
      cost_of_running(0.5),
      cost_of_running(0.45)
    )


class TestMinettiWalk(unittest.TestCase):
  def test_below_range(self):
    self.assertEqual(
      cost_of_walking(-0.5),
      cost_of_walking(-0.45)
    )

  def test_above_range(self):
    self.assertEqual(
      cost_of_walking(0.5),
      cost_of_walking(0.45)
    )
