import numpy as np


def poly_5(x, a, b, c, d, e, f):
  """Generic 5th-order polynomial function.
  
  Args:
    x (float or array(float)): the quantity to apply the polynomial to.
      Could be a single value, a numpy array, or a pandas Series.
    a (float): coefficient for the fifth-order term.
    b (float): coefficient for the fourth-order term.
    c (float): coefficient for the third-order term.
    d (float): coefficient for the second-order term.
    e (float): coefficient for the first-order term.
    f (float): coefficient for the zeroth-order term.

  Returns:
    float
  """
  return a * x ** 5 + b * x ** 4 + c * x ** 3 + d * x ** 2 + e * x + f


def cost_of_running(decimal_grade):
  """Energy consumption of running (per kg per m), according Minetti 2002.

  This is the curve fit supplied by the authors of the paper.

  It applies to slopes <= 45%.

  Args:
    decimal_grade (float): decimal grade of terrain, i.e. 0.2 for 20%.
    equation (str): 
  Returns:
    float: the estimated cost of running, in J/kg/m, at the given grade.
  """
  # Constrain decimal grade to the range of the equation's validity
  decimal_grade = np.clip(decimal_grade, -0.45, 0.45)

  return poly_5(decimal_grade, 155.4, -30.4, -43.3, 46.3, 19.5, 3.6)


def cost_of_walking(decimal_grade):
  """Energy consumption of walking (per kg per m), according Minetti 2002.

  This is the curve fit supplied by the authors of the paper.

  NOTE: Energy consumption varied with walking speed, and this equation
  represents the minimum energy consumption as a function of grade.

  Args:
    decimal_grade (float): decimal grade of terrain, i.e. 0.2 for 20%.
    equation (str): 
  Returns:
    float: the estimated cost of walking, in J/kg/m, at the given grade.
  """
  # Constrain decimal grade to the range of the equation's validity
  decimal_grade = np.clip(decimal_grade, -0.45, 0.45)

  return poly_5(decimal_grade, 280.5, -58.7, -76.8, 51.9, 19.6, 2.5)