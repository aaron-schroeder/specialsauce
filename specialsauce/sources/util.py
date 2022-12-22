def constrain_grade(decimal_grade, min_grade, max_grade):
  return min(max_grade, max(min_grade, decimal_grade))
