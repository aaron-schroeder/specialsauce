import unittest

import pandas as pd

from specialsauce.datasets import load_ngp_gap


class TestDatasets(unittest.TestCase):
    def test_load_ngp_gap(self):
        data = load_ngp_gap()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertTrue(all(
            [pd.api.types.is_timedelta64_dtype(dtype) 
             for dtype in data.dtypes]
        ))