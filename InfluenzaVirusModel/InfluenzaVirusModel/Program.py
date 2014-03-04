import Systems
import random
import time
import thread
import Config
from Graph import Graph, OverallSimulationDataGraph, SimulationData, FociAreaGraph
from SimulationVisualization import SimVis
from Worldspace import Worldsite, Vector2d
import Worldspace
import Cells
import thread
import Config
from Logger import StdOutLogger as Log
 
from threading import Thread  # threading is better than the thread module
from Queue import Queue

q = Queue()  # use a queue to pass messages from the worker thread to the main thread
running = [True]
RNG = random

class MainProgram:     

    # TODO: Figure out a better way of passing settings. Cleanup this method.
    def run(self, settings):
        """Main loop."""

        self.avgFociAreaMM2 = None

        if Graph.SHOW:
            data = SimulationData()
            graph = OverallSimulationDataGraph()
            graph.setXMeasurement('hours') 
            graph.setTimestepsInXMeasurement(6)
            
            fociAreaGraph = FociAreaGraph()
            #fociAreaGraph = FociAreaGraph(True, Worldspace.GRID_WIDTH, Worldspace.GRID_HEIGHT)
            fociAreaGraph.setXMeasurement('hours') 
            fociAreaGraph.setTimestepsInXMeasurement(6)

        if SimVis.ENABLED:
            q.put((simVis.display, (), {}))
        
        self.numberOfRuns = settings["iNumberOfRuns"]
        self.runTime = settings["iRunTime"]
        self.debugTextEnabled = settings["bDebugTextEnabled"]

        #initialise runs
        run = 0
        while run < self.numberOfRuns:

            if self.debugTextEnabled:
                startTime = time.clock()
                Log.out("Start time: %s" % startTime)
            
            #re-initialize world and systems if not on the initial run
            world = []
            for x in xrange(Worldspace.GRID_WIDTH):
                world.append([])
                for y in xrange(Worldspace.GRID_HEIGHT):
                    world[x].append(Worldsite(Vector2d(x, y)))   

            eSys = Systems.EpithelialSystem(world)
            immSys = Systems.ImmuneSystem(world)

            eSys.initialise()
            if(Systems.ImmuneSystem.ISENABLED):
                immSys.initialise()
            
            if Graph.SHOW:
                graph.setTotalEpithelialCells(Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT)
                graph.setBaseImmuneCells(immSys.INIT_CELLS)

                graph.initRun()
                fociAreaGraph.initRun()
            
            if SimVis.ENABLED:
                simVis.init(world, run + 1)

            # Run simulation for a given number of timesteps
            # 10 days = 1440 timesteps
            timesteps = 0
            while timesteps <= self.runTime:
                eSys.update()
                if(Systems.ImmuneSystem.ISENABLED):
                    immSys.update()

                eSys.synchronise()
                if(Systems.ImmuneSystem.ISENABLED):
                    immSys.synchronise()

                if Graph.SHOW:
                    data.time             = timesteps
                    data.eCellsHealthy    = eSys.healthyCount
                    data.eCellsContaining = eSys.containingCount
                    data.eCellsExpressing = eSys.expressingCount
                    data.eCellsInfectious = eSys.infectiousCount
                    data.eCellsDead       = eSys.naturalDeathCount + eSys.infectionDeathCount
                    data.immCellsTotal    = immSys.virginCount + immSys.matureCount

                    graph.addSimulationData(data)

                    if(Systems.FocusSystem.ENABLED):
                        area = 0.0
                        c = 0
                        for foci in eSys.fSys.foci.values() :
                            if foci.isEnabled :
                                if foci.cellCount != 0 :
                                    area += foci.cellCount
                                    c += 1
                        if c == 0 :
                            area = 0
                        else :
                            area = area / c
                        self.avgFociAreaMM2 = fociAreaGraph.addAverageFociAreaData(area, timesteps)


                if self.debugTextEnabled:
                    Log.out('%d: %d' %(run + 1, timesteps))
                    Log.out("Infected cells: %s" % (eSys.containingCount + eSys.expressingCount + eSys.infectiousCount))
                    Log.out("Healthy: %s" % (eSys.healthyCount))
                    Log.out("Containing: %s" % (eSys.containingCount))
                    Log.out("Expressing: %s" % (eSys.expressingCount))
                    Log.out("Infectious: %s" % (eSys.infectiousCount))
                    Log.out("Dead: %s" % (eSys.naturalDeathCount + eSys.infectionDeathCount))
                    Log.out("Virgin: %s" % (immSys.virginCount))
                    Log.out("Mature: %s" % (immSys.matureCount))
                    if Systems.FocusSystem.ENABLED and self.avgFociAreaMM2 != None :
                    #Log.out("Average focus area: %s" % (eSys.avgFociArea))
                        Log.out("Average focus area (mm2): %s" % (self.avgFociAreaMM2))
                    Log.out("\n")

                if SimVis.ENABLED:
                    if timesteps == 0 or timesteps % 72 == 0 :
                        simVis.drawSimWorld(True, timesteps)
                    else :
                        simVis.drawSimWorld(False, timesteps)

                    if Systems.FocusSystem.ENABLED:     
                        if len(eSys.fSys.mergeDetected) > 0:
                            for i in xrange(len(eSys.fSys.mergeDetected) - 1, -1, -1):
                                if SimVis.HIGHLIGHT_COLLISIONS:
                                    focus = eSys.fSys.mergeDetected[i]
                                    for perimeterCell in focus.perimeter:
                                        simVis.drawCollision(perimeterCell)

                                del eSys.fSys.mergeDetected[i]
                    
                            # HACK: For debugging/testing purposes. Will be removed/refactored soon.
                            if SimVis.HIGHLIGHT_COLLISIONS and SimVis.ENABLED:
                                simVis._SimVis__savePILImageToFile(False)
                                simVis._SimVis__updateCanvas(False)
                                #if Systems.FocusSystem.DEBUG_TEXT_ENABLED:
                                    #raw_input()

                timesteps += 1

            if(Systems.FocusSystem.ENABLED):
                if self.debugTextEnabled :
                    out = "remaining usable foci: "
                    c = 0
                    for focus in eSys.fSys.foci.values() :
                        if focus.isEnabled and focus.cellCount > 0:
                            c += 1
                            out += str(focus.id) + ", "
                    Log.out(out + " count = " + str(c) +"\n")
            
            if self.debugTextEnabled:
                endTime = time.clock()
                Log.out("End time: %s" % endTime)
                Log.out("Elapsed time: %s" % (endTime - startTime))

            #increment run
            run += 1

        # All runs finished: display results graph
        if Graph.SHOW:
            if(Systems.FocusSystem.ENABLED):
                q.put((fociAreaGraph.showGraph, ([True]), {}))
            q.put((graph.showGraph, ([True]), {}))
        running = False

# TODO: Sort out this messy startup definition
if __name__ == "__main__":
    config = Config.ConfigReader()
    settings = config.SetConfiguration()

    if SimVis.ENABLED:
        if SimVis.SNAPSHOT_ENABLED:
            width = SimVis.SNAPSHOT_WIDTH if SimVis.SNAPSHOT_WIDTH <= Worldspace.GRID_WIDTH else Worldspace.GRID_WIDTH
            height = SimVis.SNAPSHOT_HEIGHT if SimVis.SNAPSHOT_HEIGHT <= Worldspace.GRID_HEIGHT else Worldspace.GRID_HEIGHT

            simVis = SimVis(width, height, SimVis.SQUARESIZE) # snapshot
        else:
            simVis = SimVis(Worldspace.GRID_WIDTH, Worldspace.GRID_HEIGHT, SimVis.SQUARESIZE) # full sim size
        simVis.setTimeMeasurement("hours")
        simVis.setTimeStepsInMeasurement(6.0)

    thread.start_new_thread(MainProgram().run, (settings,))
    while running:
        # now the main thread doesn't care what function it's executing.
        # previously it assumed it was sending the message to display().
        f, args, kwargs = q.get()
        f(*args, **kwargs)
        q.task_done()