import unittest
from Graph import Graph, OverallSimulationDataGraph, SimulationData
import random

class GraphTest(unittest.TestCase):
    def test_data_init(self):
        data = SimulationData()
        self.assertIsNotNone(data)
        self.assertEquals(data.time, 0)
        self.assertEquals(data.eCellsHealthy, 0)
        self.assertEquals(data.eCellsContaining, 0)
        self.assertEquals(data.eCellsExpressing, 0)
        self.assertEquals(data.eCellsInfectious, 0)
        self.assertEquals(data.eCellsDead, 0)
        self.assertEquals(data.immCellsTotal, 0)
        self.assertEquals(data.eCellsInfected, None)

    def test_graph_init(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)
        self.assertEquals(graphVis.totalECells, 0.0)
        self.assertEquals(graphVis.baseImmCells, 0.0)
        self.assertEquals(graphVis.time, [])
        self.assertEquals(graphVis.healthyResultsList, [])
        self.assertEquals(graphVis.containingResultsList, [])
        self.assertEquals(graphVis.expressingResultsList, [])
        self.assertEquals(graphVis.infectiousResultsList, [])
        self.assertEquals(graphVis.deadResultsList, [])
        self.assertEquals(graphVis.immCellsResultsList, [])
        self.assertEquals(graphVis.infectedResultsList, [])
        self.assertEquals(graphVis.index, -1)

        with self.assertRaises(AttributeError):
            OverallSimulationDataGraph(1)
        with self.assertRaises(AttributeError):
            OverallSimulationDataGraph(1, 2, 3)

        graphVis = OverallSimulationDataGraph(0, 100)
        self.assertIsNotNone(graphVis)
        self.assertEquals(graphVis.totalECells, 0)
        self.assertEquals(graphVis.baseImmCells, 100)

        with self.assertRaises(AttributeError):
            OverallSimulationDataGraph(-1, -2)

    def test_graph_setTotalEpithelialCells(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)
        self.assertEquals(graphVis.totalECells, 0.0)

        graphVis.setTotalEpithelialCells(1)
        self.assertEquals(graphVis.totalECells, 1)
        with self.assertRaises(AttributeError):
            graphVis.setTotalEpithelialCells(-1)

    def test_graph_setBaseImmuneCells(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)
        self.assertEquals(graphVis.baseImmCells, 0.0)

        graphVis.setBaseImmuneCells(1)
        self.assertEquals(graphVis.baseImmCells, 1)
        with self.assertRaises(AttributeError):
            graphVis.setBaseImmuneCells(-1)

    def test_graph_setInitialSimlulationData(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)
        self.assertEquals(graphVis.totalECells, 0.0)
        self.assertEquals(graphVis.baseImmCells, 0.0)

        graphVis.setInitialSimlulationData(1, 2)
        self.assertEquals(graphVis.totalECells, 1)
        self.assertEquals(graphVis.baseImmCells, 2)

        with self.assertRaises(AttributeError):
            graphVis.setInitialSimlulationData(-1, -2)

    def test_graph_addSimulationData(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)

        data = SimulationData()
        data.time = 1
        data.eCellsHealthy = 2
        data.eCellsContaining = 3
        data.eCellsExpressing = 4
        data.eCellsInfectious = 5
        data.eCellsDead = 6
        data.immCellsTotal = 7
        data.eCellsInfected = 8

        with self.assertRaises(AttributeError):
            graphVis.addSimulationData(data)

        graphVis.initRun()
        graphVis.addSimulationData(data)
        
        self.assertEquals(graphVis.time[0], 1)
        self.assertEquals(graphVis.healthyResultsList[0][0], 2)
        self.assertEquals(graphVis.containingResultsList[0][0], 3)
        self.assertEquals(graphVis.expressingResultsList[0][0], 4)
        self.assertEquals(graphVis.infectiousResultsList[0][0], 5)
        self.assertEquals(graphVis.deadResultsList[0][0], 6)
        self.assertEquals(graphVis.immCellsResultsList[0][0], 7)
        self.assertEquals(graphVis.infectedResultsList[0][0], 8)


    def test_graph_addDataTo(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)

        arr1 = []
        graphVis._Graph__addDataTo(1, arr1)
        self.assertEquals(arr1[0], 1)

        #test null values are allowed (duplicates previous value)
        graphVis._Graph__addDataTo(None, arr1)
        self.assertEquals(arr1, [1, 1])
        #test negative throws exception
        with self.assertRaises(AttributeError):
            graphVis._Graph__addDataTo(-1, graphVis.time)

    def test_graph_normalizeECellData(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)

        ls = [-1.0, 0.0, 1.0, 2.0, 3.0]
        #test totalECells not set throws exception
        with self.assertRaises(AttributeError):
            graphVis._OverallSimulationDataGraph__normalizeECellData(ls)

        graphVis.totalECells = 10.0
        graphVis._OverallSimulationDataGraph__normalizeECellData(ls)
        self.assertEquals(ls, [0.0, 0.0, 0.1, 0.2, 0.3])

    def test_graph_normalizeImmCellData(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)

        ls = [-1.0, 0.0, 1.0, 10.0, 100.0, 1000.0]
        #test totalECells not set throws exception
        #with self.assertRaises(AttributeError):
        #    graphVis._OverallSimulationDataGraph__normalizeImmCellData(ls)
        # Note: no longer raises exception as having no immune cells is available option

        graphVis.baseImmCells = 10.0
        ls = [-1.0, 0.0, 1.0, 10.0, 100.0, 1000.0, 10000.0]
        graphVis._OverallSimulationDataGraph__normalizeImmCellData(ls)
        self.assertEquals(ls, [0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2])

    def test_graph_normalizeTimeFromStepsToDays(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)

        ls = [-1.0, 0.0, 1.0, 2.0, 3.0]
        val = graphVis.timestepsInX
        graphVis._Graph__normalizeTimeFromStepsToDays(ls)
        self.assertEquals(ls, [-1.0/val, 0.0/val, 1.0/val, 2.0/val, 3.0/val])

        newVal = 144
        graphVis.setTimestepsInXMeasurement(newVal)
        val = graphVis.timestepsInX
        self.assertEquals(newVal, val)
        graphVis._Graph__normalizeTimeFromStepsToDays(ls)
        self.assertEquals(ls, [-1.0/val, 0.0/val, 1.0/val, 2.0/val, 3.0/val])


    def test_graph_normalizeDataBy(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)

        arr = [0, 10, 50, 100]
        graphVis._Graph__normalizeDataBy(arr, 0, 100)
        self.assertEquals(arr, [0.0, 10.0, 50.0, 100.0])


    # Please Note: this test will show a graph on ui thread, will have to close the graph for other tests to complete
    # comment out this test if you do not wish to run UI tests (user testing)
    def test_graph_showGraph(self):
        graphVis = OverallSimulationDataGraph()
        self.assertIsNotNone(graphVis)

        graphVis.showGraph(False)

    def test_graph_initRun(self):
        graphVis = OverallSimulationDataGraph()
        self.assertEquals(graphVis.index, -1)

        time = [0,1,2]
        healthyArr = [3,4,5]
        containingArr = [6,7,8]
        expressingArr = [9,10,11]
        infectiousArr = [11,12,13]
        deadArr = [13,14,15]
        immuneArr = [16,17,18]
        infectedArr = [19,20,21]

        graphVis.time = time
        graphVis.healthyResultsList = [healthyArr]
        graphVis.containingResultsList = [containingArr]
        graphVis.expressingResultsList = [expressingArr]
        graphVis.infectiousResultsList = [infectiousArr]
        graphVis.deadResultsList = [deadArr]
        graphVis.immCellsResultsList = [immuneArr]
        graphVis.infectedResultsList = [infectedArr]

        graphVis.initRun();
        
        self.assertEquals(graphVis.time, time)
        self.assertEquals(graphVis.healthyResultsList, [healthyArr, []])
        self.assertEquals(graphVis.containingResultsList,[containingArr, []])
        self.assertEquals(graphVis.expressingResultsList,[expressingArr, []])
        self.assertEquals(graphVis.infectiousResultsList,[infectiousArr, []])
        self.assertEquals(graphVis.deadResultsList,[deadArr, []])
        self.assertEquals(graphVis.immCellsResultsList,[immuneArr, []])
        self.assertEquals(graphVis.infectedResultsList,[infectedArr, []])

        self.assertEquals(graphVis.index, 0)

    # Please Note: this test will show a graph on ui thread, will have to close the graph for other tests to complete
    # comment out this test if you do not wish to run UI tests (user testing)
    def test_graph_simulation_usage(self):
        graphVis = OverallSimulationDataGraph()
        graphVis.setTotalEpithelialCells(10000)
        graphVis.setBaseImmuneCells(10)
        graphVis.initRun()
        data = SimulationData()
        self.assertIsNotNone(data)
        for i in xrange(0, 10000):
            data.time = i
            data.eCellsHealthy = 10000 - i
            data.eCellsContaining = i / 3.0
            data.eCellsExpressing = i / 3.0
            data.eCellsInfectious = i / 3.0
            data.eCellsDead = i

            if i < 1000 :
                data.immCellsTotal = 10
            elif i < 3000 :
                data.immCellsTotal = 10 + (i - 1000)
            elif i < 8000 :
                data.immCellsTotal = 2000
            else :
                data.immCellsTotal = 10 + (10000 - i)

            graphVis.addSimulationData(data)
        
        print(str(graphVis.baseImmCells))
        graphVis.showGraph(True)


    def test_mutiplePlots(self):
        graphVis = OverallSimulationDataGraph()
        data = SimulationData()

        graphVis.time = [0,1,2,3,4,5,6,7,8,9,10]
        print(graphVis.index)
        graphVis.initRun();
        graphVis.infectedResultsList[graphVis.index] = [2,3,4,5,6,7,8,9,10,11,12]
        print(graphVis.index)
        graphVis.initRun();
        graphVis.infectedResultsList[graphVis.index] = [4,5,6,7,8,9,10,11,12,13,14]
        print(graphVis.index)
        graphVis.initRun();  
        graphVis.infectedResultsList[graphVis.index] = [6,7,8,9,10,11,12,13,14,15,16]
        print(graphVis.index)

        print graphVis.infectedResultsList

        with self.assertRaises(AttributeError):
            graphVis.showGraph(True)

        graphVis.setTotalEpithelialCells(20)

        graphVis.showGraph(True)

