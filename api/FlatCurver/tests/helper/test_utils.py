import unittest
import pandas as pd

from ...helper.utils import arrange_dates

class TestMatrixCreatorHelper(unittest.TestCase):

    @classmethod
    def setUp(cls) -> None:
        cls.indict = {"2020-01-01": 1, "2020-02-01": 10, "2020-03-01": 15}
        cls.timesteps = 100

    def test_arrange_dates(self):
        srs = arrange_dates(self.indict, self.timesteps)
        expected_keys = pd.date_range("2020-01-01", periods=self.timesteps)
        expected_values = [1] * 31 + [10] * 29 + [15] * 40
        expected_srs = pd.Series(expected_values, index=expected_keys)
        pd.testing.assert_series_equal(srs, expected_srs)

    def test_arange_dates_shorter_then_last_date(self):
        timesteps = 20
        srs = arrange_dates(self.indict, timesteps=timesteps)
        expected_keys = pd.date_range("2020-01-01", periods=timesteps)
        expected_values = [1] * 20
        expected_srs = pd.Series(expected_values, index=expected_keys)
        pd.testing.assert_series_equal(srs, expected_srs)

