import unittest
import Systems
from Worldspace import Worldsite, Vector2d
import Cells
import Worldspace

class Test_tests_systems(unittest.TestCase):
    def setUp(self):

        Systems.ImmuneSystem.BASE_IMM_CELL = 0.00015
        
        Systems.EpithelialSystem.INFECT_INIT = 0.01
        Worldspace.GRID_WIDTH = 3
        Worldspace.GRID_HEIGHT = 3
        Cells.ImmuneCell.IMM_LIFESPAN = 1008
        
        self.world = []
        for x in xrange(Worldspace.GRID_WIDTH):
            self.world.append([])
            for y in xrange(Worldspace.GRID_HEIGHT):
                 self.world[x].append(Worldsite(Vector2d(x, y)))

        self.eSys = Systems.EpithelialSystem(self.world)
        self.iSys = Systems.ImmuneSystem(self.world)

    def test_worldCreationTest(self):

        # Check world size
        self.assertEquals(len(self.world), Worldspace.GRID_WIDTH)
        for x in xrange(len(self.world)):
            self.assertEquals(len(self.world[x]), Worldspace.GRID_HEIGHT)

        
    def test_systemsInitialisation(self):
        # Check cell instantiation
        self.eSys.initialise()
        self.iSys.initialise()
        eCellCounter = 0
        iCellCounter = 0
        predictedImmCellCount = int((Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT) * Systems.ImmuneSystem.BASE_IMM_CELL) if int((Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT) * Systems.ImmuneSystem.BASE_IMM_CELL) > 1 else 1
        for x in xrange(len(self.world)):
            for y in xrange(len(self.world[x])):
                self.failIf(type(self.world[x][y].eCell) != Cells.EpithelialCell)
                    
                eCellCounter += 1
                if len(self.world[x][y].immCells) > 0:
                    iCellCounter += len(self.world[x][y].immCells)
                    for z in xrange(len(self.world[x][y].immCells)):
                        self.failIf(type(self.world[x][y].immCells[z]) != Cells.ImmuneCell)

        self.assertEquals(eCellCounter, Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT)
        self.assertEquals(iCellCounter, predictedImmCellCount)

        

