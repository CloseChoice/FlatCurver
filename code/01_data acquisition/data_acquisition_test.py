"""Fetch historical covid-19 data from multpile sources."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# system packages
import unittest

# internal packages
from data_acquisition import DataAcquisition

class TestStringMethods(unittest.TestCase):

  def fetch_germany_morgenpost(self):
    data_acquisition = DataAcquisition()
    df = data_acquisition.fetch_germany_morgenpost()
    self.assertGreater(df.shape[0], 0)
    self.assertGreater(df.shape[1], 0)

  def test_fetch_bundesland_morgenpost(self):
    data_acquisition = DataAcquisition()
    df = data_acquisition.fetch_bundesland_morgenpost("Bayern")
    self.assertGreater(df.shape[0], 0)
    self.assertGreater(df.shape[1], 0)

  def fetch_fetch_bundesland_rki(self):
    data_acquisition = DataAcquisition()
    df = data_acquisition.fetch_bundesland_rki("Bayern")
    self.assertGreater(df.shape[0], 0)
    self.assertGreater(df.shape[1], 0)

if __name__ == '__main__':
    unittest.main()