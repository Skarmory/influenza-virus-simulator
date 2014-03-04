from abc import ABCMeta, abstractmethod
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import math 
import numpy as np
import SimUtils

class Graph(object):
    """Class for displaying Simulation Data into a graph"""

    SHOW = None

    __metaclass__ = ABCMeta

    def __init__(self):
        self.xMeasure = "timesteps"
        self.timestepsInX = 1.0
        
        self.index = -1

        self.time = []

        self.folderName = "images/"
        SimUtils.initFolder(folderName=self.folderName)

        self.graphFileName = "simulation_graph"

    def __normalizeDataBy(self, dataArr, normMin, normMax):
        """Normalize some array of data by given normalize values"""
        if dataArr == None :
            raise AttributeError('dataArr is null')
        if normMin == None :
            raise AttributeError('normMin is null')
        if normMax == None :
            raise AttributeError('normMax is null')
        if normMin > normMax :
            raise AttributeError('normMin must not be less than normMax')

        maxVal = dataArr[0]
        minVal = dataArr[0]
        for res in dataArr :
            if res > maxVal :
                maxVal = res
            if res < minVal :
                minVal = res

        l = len(dataArr)
        for i in xrange(0, l) :
            dataArr[i] = float(normMin) + (float(dataArr[i]) - float(minVal)) * (float(normMax) - float(normMin)) / (float(maxVal) - float(minVal))

    def getStandardDeviationValues(self, lists):
        if lists == None :
            raise AttributeError('lists is null')
        if len(lists) == 0 :
            #lists is empty, dont throw an exeption just return None
            return None

        minimums = []
        maximums = []

        numLists = len(lists)
        mean = 0.0
        std = 0.0
        max = 0.0
        min = 0.0
        val = 0.0
        tempList = []

        length = len(lists[0]) # assuming all same length
        for i in xrange(0, length) :
            del tempList[:]
            for j in xrange(0, numLists) :
                val = lists[j][i]
                tempList.append(val)
            mean = np.mean(tempList)
            std = np.std(tempList)

            min = mean - std
            max = mean + std

            maximums.append(max)
            minimums.append(min)

        result = [minimums, maximums]
        return result


    def getMinsMaxs(self, lists) :
        if lists == None :
            raise AttributeError('lists is null')
        if len(lists) == 0 :
            #lists is empty, dont throw an exeption just return None
            return None

        minimums = []
        maximums = []

        numLists = len(lists)
        max = 0.0
        min = 0.0
        val = 0.0
        val0 = 0.0

        length = len(lists[0]) # assuming all same length
        for i in xrange(0, length) :
            val0 = lists[0][i]
            min = val0
            max = val0
            for j in xrange(0, numLists) :
                val = lists[j][i]
                if val > max :
                    max = val
                if val < min :
                    min = val

            maximums.append(max)
            minimums.append(min)

        result = [minimums, maximums]
        return result

    def __addDataTo(self, data, dataArr):
        """Add some data to the specified data array"""
        if dataArr == None :
            raise AttributeError('dataArr is null')
        if data != None :
            if data < 0 :
                raise AttributeError('data must be greater than or equal 0')
            dataArr.append(data)
        elif len(dataArr) > 0:
            dataArr.append(dataArr[len(dataArr) - 1])

    
    def __normalizeTimeFromStepsToDays(self, dataArr) :
        if dataArr == None :
            raise AttributeError('dataArr is null')
        l = len(dataArr)
        for i in xrange(0, l) :
            # timesteps to hour, default = 6. therefore timesteps to day = 144
            dataArr[i] = (float(dataArr[i]) / self.timestepsInX)

            
    def setXMeasurement(self, xMeasure):
        self.xMeasure = xMeasure

    def setTimestepsInXMeasurement(self, timestepsInX):
        self.timestepsInX = timestepsInX

    @staticmethod
    def plotData(arr):
        plt.plot(arr)
        plt.show()

    @staticmethod
    def Configure(settings):
        Graph.SHOW = settings["bShowGraphOnFinish"]

    @abstractmethod
    def showGraph(normalize):
        pass

    @abstractmethod
    def initRun():
        pass

class OverallSimulationDataGraph(Graph):
    def __init__(self, *args):
        """
        GraphVisualization Constructor:
        Can take no arguments, or 2 arguments (totalECells, baseImmCells).
        If no arguments are given totalECells and baseImmCells will need to be set before displaying graph.
        """
        super(OverallSimulationDataGraph, self).__init__()

        self.totalECells = 0.0
        self.baseImmCells = 0.0
        numArgs = len(args)
        if numArgs > 0 :
            if numArgs == 2 :
                self.setInitialSimlulationData(args[0], args[1])
            else :
                raise AttributeError('__init__ must take either zero arguments or 2 arguments (totalECells, baseImmCells)')

        self.healthyResultsList = []
        self.containingResultsList = []
        self.expressingResultsList = []
        self.infectiousResultsList = []
        self.deadResultsList = []
        self.immCellsResultsList = []
        self.infectedResultsList = []

    def setInitialSimlulationData(self, totalECells, baseImmCells):
        """Set the initial simulation data for the simulation (totalECells and baseImmCells)"""
        self.setTotalEpithelialCells(totalECells)
        self.setBaseImmuneCells(baseImmCells)

    def setTotalEpithelialCells(self, totalECells):
        """Set the total number of Epithelial Cells in the simulation"""
        if totalECells == None :
            raise AttributeError('totalECells is null')
        if totalECells < 0 :
            raise AttributeError('totalECells must be greater than or equal 0')
        self.totalECells = totalECells

    def setBaseImmuneCells(self, baseImmCells):
        """Set the inital of Immune Cells in the simulation"""
        if baseImmCells == None :
            raise AttributeError('baseImmCells is null')
        if baseImmCells < 0 :
            raise AttributeError('baseImmCells must be greater than or equal 0')
        self.baseImmCells = baseImmCells

    def addSimulationData(self, data):
        """Adds all of the values contained withing a SimulationData object to their respective arrays"""
        if data == None :
            raise AttributeError('data is null')
        if self.index < 0 :
            raise AttributeError('index is less than zero - have you called initRun()?')
        if self.index == 0:
            self._Graph__addDataTo(data.time, self.time)
        self._Graph__addDataTo(data.eCellsHealthy, self.healthyResultsList[self.index])
        self._Graph__addDataTo(data.eCellsContaining, self.containingResultsList[self.index])
        self._Graph__addDataTo(data.eCellsExpressing, self.expressingResultsList[self.index])
        self._Graph__addDataTo(data.eCellsInfectious, self.infectiousResultsList[self.index])
        self._Graph__addDataTo(data.eCellsDead, self.deadResultsList[self.index])
        self._Graph__addDataTo(data.immCellsTotal, self.immCellsResultsList[self.index])

        if data.eCellsInfected != None :
            self._Graph__addDataTo(data.eCellsInfected, self.infectedResultsList[self.index])
        else :
            self._Graph__addDataTo(data.eCellsContaining + data.eCellsExpressing + data.eCellsInfectious, self.infectedResultsList[self.index])

    def __normalizeECellData(self, dataArr) :
        if dataArr == None :
            raise AttributeError('dataArr is null')
        if self.totalECells == 0.0 :
            raise AttributeError('totalECells must be greater than 0')
        l = len(dataArr)
        for i in xrange(0, l) :
            newValue = (float(dataArr[i]) / float(self.totalECells))
            if newValue < 0 :
                newValue = 0.0
            if newValue > 1 :
                newValue = 1.0
            dataArr[i] = newValue

    def __normalizeImmCellData(self, dataArr) :
        if dataArr == None :
            raise AttributeError('dataArr is null')
        if self.baseImmCells == 0.0 :
            #raise AttributeError('baseImmCells must be greater than 0')
            return

        l = len(dataArr)
        for i in xrange(0, l) :
            # normalized 10x10^? ? being 2 in there example, signifying a 1000-fold increase. 10x10^2 = 1000
            # log( (immCells / baseImmCells) - baseImmCells)
            fractionImmCellsOverBase = (float(dataArr[i])) / float(self.baseImmCells)
            if (fractionImmCellsOverBase / 10.0) < 1 : # < 0 cant do log, < 1 log is negative (only want positive)
                 dataArr[i] = 0.0
            else :
                newValue = math.log10(fractionImmCellsOverBase / 10.0) / 10.0
                if newValue < 0 :
                    newValue = 0.0
                if newValue > 1 :
                    newValue = 1.0
                dataArr[i] = newValue


    def initRun(self):
        '''
        Convinience method for setting a run to complete.
        This is used at the end of a simulation run in order to plot normalized data for multiple runs.
        '''
        self.index += 1

        self.healthyResultsList.append([])
        self.infectedResultsList.append([])
        self.containingResultsList.append([])
        self.expressingResultsList.append([])
        self.infectiousResultsList.append([])
        self.deadResultsList.append([])
        self.immCellsResultsList.append([])

    def __subplot(self, lists, normalize, color, labelStr):
        minsmaxs = self.getStandardDeviationValues(lists)
        if minsmaxs != None :

            mins = minsmaxs[0]
            maxs = minsmaxs[1]

            if len(mins) == 0 or len(maxs) == 0 :
                return

            if normalize and lists != self.immCellsResultsList:
                self.__normalizeECellData(maxs)
                self.__normalizeECellData(mins)
            else :
                self.__normalizeImmCellData(maxs)
                self.__normalizeImmCellData(mins)
             
            #ax = plt.subplot()
            #ax.plot(self.time, maxs, label=labelStr, color=color)
            #ax.fill_between(self.time, mins, maxs, facecolor=color, color=color)

            self.ax.plot(self.time, maxs, label=labelStr, color=color)
            self.ax.fill_between(self.time, mins, maxs, facecolor=color, color=color)

    def showGraph(self, normalize):
        self.ax = plt.subplot()
        if normalize :
            self._Graph__normalizeTimeFromStepsToDays(self.time)

        self.__subplot(self.healthyResultsList, normalize, 'grey', 'healthy epithelial cells')
        self.__subplot(self.infectedResultsList, normalize, 'saddlebrown', 'infected epithelial cells')
        self.__subplot(self.containingResultsList, normalize, 'yellow', 'containing epithelial cells')
        self.__subplot(self.expressingResultsList, normalize, 'orange', 'expressing epithelial cells')
        self.__subplot(self.infectiousResultsList, normalize, 'red', 'infectious epithelial cells')
        self.__subplot(self.deadResultsList, normalize, 'black', 'dead epithelial cells')
        self.__subplot(self.immCellsResultsList, normalize, 'green', 'total immune cells')


        self.__showGraph()

    def __showGraph(self):
        plt.title("Overall Simulation Data Graph")
        fontP = FontProperties()
        fontP.set_size('small')

        plt.ylabel('% Total Cells')
        plt.xlabel('Time (' + self.xMeasure + ')')

        ##DEFAULTS
        #    #left  = 0.125  # the left side of the subplots of the figure
        #    #right = 0.9    # the right side of the subplots of the figure
        #    #bottom = 0.1   # the bottom of the subplots of the figure
        #    #top = 0.9      # the top of the subplots of the figure
        #    #wspace = 0.2   # the amount of width reserved for blank space between subplots
        #    #hspace = 0.2   # the amount of height reserved for white space between subplots
        plt.subplots_adjust(left=0.125, bottom=0.15, right=0.9, top=0.94, wspace=0.2, hspace=0.2)

        # Shink current axis's height by 10% on the bottom
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])

        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12),
                  fancybox=True, shadow=True, ncol=3, prop=fontP)

        plt.savefig(self.folderName + self.graphFileName)
        plt.show()


class SimulationData(object):
    """
    Data structure for simulation data.
    Can be passed to GraphVisualization object to update simulation results for producing graphs.
    """
    def __init__(self):
        """description of method"""
        self.time = 0.0
        self.eCellsHealthy = 0.0
        self.eCellsInfected = None
        self.eCellsContaining = 0.0
        self.eCellsExpressing = 0.0
        self.eCellsInfectious = 0.0
        self.eCellsDead = 0.0
        self.immCellsTotal = 0.0

class FociAreaGraph(Graph):

    CELLS_PER_PETRI_DISH_95MM = 1430000.00
    CELL_AREA_MM2 = 1.0/15000.0
    CELLS_PER_SITE_DEFAULT = 143.0

    def __init__(self, scaleByGridSize=False, gridWidth=None, gridHeight=None):
        super(FociAreaGraph, self).__init__()
        self.fociAreaList = []
        self.graphFileName = "foci_area_graph"
        if scaleByGridSize :
            self.scaledCellArea = FociAreaGraph.getScaledCellAreaForGridSize(gridWidth, gridHeight)
        else :
            self.scaledCellArea = FociAreaGraph.CELLS_PER_SITE_DEFAULT * FociAreaGraph.CELL_AREA_MM2

    def addAverageFociAreaData(self, avgFociAreaCells, time):
        avgFociAreaMM2 = avgFociAreaCells * self.scaledCellArea
        #print(str(avgFociArea)) # for debugging

        self.fociAreaList[self.index].append(avgFociAreaMM2)
        if self.index == 0 :
            self.time.append(time)

        return avgFociAreaMM2

    def showGraph(self, normalize):

        if normalize :
            self._Graph__normalizeTimeFromStepsToDays(self.time)

        self.__subplot(self.fociAreaList, 'blue', 'Average Foci Area (mm2)')

        #plt.title("foci area graph")
        #plt.plot(self.time, self.fociAreaArr)
        #plt.ylabel('average foci area (mm2)')
        #plt.xlabel('time (' + self.xMeasure + ')')
        #plt.show()
        self.__showGraph()

    def __showGraph(self):
        plt.title("Foci Area Graph")      
        plt.ylabel('Average Foci Area (mm2)')
        plt.xlabel('Time (' + self.xMeasure + ')')
        plt.savefig(self.folderName + self.graphFileName)
        plt.show()

    def __subplot(self, lists, color, labelStr):
        minsmaxs = self.getStandardDeviationValues(lists)
        if minsmaxs != None :

            mins = minsmaxs[0]
            maxs = minsmaxs[1]

            if len(mins) == 0 or len(maxs) == 0 :
                return
             
            ax = plt.subplot()
            ax.plot(self.time, maxs, label=labelStr, color=color)
            ax.fill_between(self.time, mins, maxs, facecolor=color, color=color)

    def initRun(self) :
        self.index += 1
        self.fociAreaList.append([])

    @staticmethod
    def getScaledCellAreaForGridSize(gridHeight, gridWidth) :
        '''
        returns what area a single \"cell\" (square) of the given grid size represents in mm2
        '''
        return (FociAreaGraph.CELLS_PER_PETRI_DISH_95MM / (gridHeight * gridWidth)) * FociAreaGraph.CELL_AREA_MM2
