import unittest

from Cells import EpithelialCell, ImmuneCell
from Worldspace import Worldsite, Vector2d

class Test_site(unittest.TestCase):
    def setUp(self):
        self.testsite = Worldsite(Vector2d(2,2))
        self.testsite.eCell = EpithelialCell(Vector2d(2,2))
        self.testsite.immCells = [ImmuneCell(Vector2d(2,2))]

    def test_location(self):
        self.failIf(not isinstance(self.testsite.location.x, int))
        self.failIf(not isinstance(self.testsite.location.y, int))

    def test_getLocation(self):
        temp = self.testsite.getLocation()
        self.failIf(not isinstance(temp, Vector2d))

    def test_getECell(self):
        temp = self.testsite.getECell()
        self.failIf(not isinstance(temp, EpithelialCell))

    def test_getImmCell(self):
        temp = self.testsite.getImmCells()
        self.failIf(not all(isinstance(x, ImmuneCell) for x in temp))