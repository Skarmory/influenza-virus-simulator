from abc import ABCMeta, abstractmethod
from Program import MainProgram, RNG
from Cells import EpithelialCell, ImmuneCell, EpithelialStates, ImmuneStates
from Worldspace import Vector2d
import Worldspace
from Logger import StdOutLogger as Log

class ISystem(object):
    """Interface for concrete systems to inherit from"""

    __metaclass__ = ABCMeta

    def __init__(self, world):
        """Constructor for ISystem

        Keyword arguments
        world -- 2d array of Worldsites
        """
        self.cells = []
        self.world = world

    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def synchronise(self):
        pass

class EpithelialSystem(ISystem):
    """The EpithelialSystem is responsible for updating and controlling all aspects of the epithelial cells in the simulation."""

    REGEN_ENABLED = INFECT_INIT = RANDOM_AGE = None
    MAX_NEIGHBOURS = 8.0

    def __init__(self, world):
        """Constructor for EpithelialSystem

        Keyword arguments
        world -- 2d array of Worldsites
        """
        ISystem.__init__(self, world)

        self.infectiousCount     = 0.0
        self.containingCount     = 0.0
        self.expressingCount     = 0.0
        self.naturalDeathCount   = 0.0
        self.infectionDeathCount = 0.0
        self.healthyCount        = 0.0
        self.avgFociArea         = 0.0
        self.initialInfected     = 0.0
        if FocusSystem.ENABLED:
            self.fSys            = FocusSystem(world)

    def initialise(self):
        """Initialisation method for EpithelialSystem, run only once when first created. Sets up the world's epithelial """
        
        initialInfected = int((Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT) * self.INFECT_INIT) if int((Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT) * self.INFECT_INIT) > 1 else 1
        self.initialInfected = initialInfected

        self.containingCount = initialInfected
        self.healthyCount    = (Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT) - initialInfected
        
        # Create epithelial cell at every site, add to system's cell list
        for i in xrange(Worldspace.GRID_WIDTH):
            for j in xrange(Worldspace.GRID_HEIGHT):
                tempECell = EpithelialCell(Vector2d(i, j))
                if EpithelialSystem.RANDOM_AGE :
                    tempECell.age = RNG.randint(0, EpithelialCell.CELL_LIFESPAN)
                self.world[i][j].eCell = tempECell
                self.cells.append(tempECell)
        
        # Set random epithelial cells to containing for initial infected count
        while initialInfected > 0:
            randomx = RNG.randint(0, Worldspace.GRID_WIDTH - 1)
            randomy = RNG.randint(0, Worldspace.GRID_HEIGHT - 1)
            tempECell = self.world[randomx][randomy].getECell()

            if tempECell.State == EpithelialStates.HEALTHY:
                tempECell.State = EpithelialStates.CONTAINING
                if FocusSystem.ENABLED:
                    self.fSys.addNewFocus(tempECell)
                initialInfected -= 1
    
    def __updateAge(self, cell):
        """Private method, should only be called from public update() method. Updates an epithelial cell's age, and updates state if necessary.
        
        Keyword arguments
        cell - An epithelial cell to update.

        Returns true if rest of update step can be skipped over.
        """

        cell.age += 1

        if cell.age >= EpithelialCell.CELL_LIFESPAN:
            EpithelialSystem.setNextState(cell, EpithelialStates.NATURAL_DEATH)
            
            return True

        return False

    def __updateRegeneration(self, cell):
        """Private method, should only be called from public update() method. Checks to see if a dead epithelial cell will regenerate.
        
        Keyword arguments
        cell - An epithelial cell to update.

        Returns true if rest of update step can be skipped over.
        """
        if self.REGEN_ENABLED:

            chance = 1

            if(self.infectionDeathCount + self.naturalDeathCount) != 0.0:
                chance = float(self.healthyCount/(self.infectionDeathCount + self.naturalDeathCount) * 1.0/EpithelialCell.DIVISION_TIME)

            if RNG.random() >= (1.0 - chance):
                EpithelialSystem.setNextState(cell, EpithelialStates.HEALTHY)
                return False
            else:
                cell.nextState = cell.State
                return True
        else:
            return True

    def __updateInfectionTime(self, cell):
        """Private method, should only be called from public update() method. Updates an epithelial cell's time infected and changes states if necessary.

        Keyword arguments
        cell - An epithelial cell to update.

        Returns true if rest of update step can be skipped over.
        """

        cell.timeInfected += 1
        if cell.timeInfected >= EpithelialCell.INFECT_LIFESPAN:
            EpithelialSystem.setNextState(cell, EpithelialStates.INFECTION_DEATH)

            return True
        return False

    def __updateInfectionSeverity(self, cell):
        """Private method, should only be called from public update() method. Increases the severity of infection by changing states if applicable.
        
        Keyword arguments
        cell - An epithelial cell to update.
        """

        if cell.State != EpithelialStates.INFECTIOUS:
            cell.delay += 1

        if cell.State == EpithelialStates.CONTAINING and cell.delay >= EpithelialCell.EXPRESS_DELAY:
            EpithelialSystem.setNextState(cell, EpithelialStates.EXPRESSING)
            return

        elif cell.State == EpithelialStates.EXPRESSING and cell.delay >= EpithelialCell.INFECT_DELAY:
            EpithelialSystem.setNextState(cell, EpithelialStates.INFECTIOUS)
            return
                
        cell.nextState = cell.State

    def __updateAttemptInfect(self, cell):
        """Private method, should only be called from public update() method. Rolls on the RNG to see whether an epithelial cell gets infected.

        Keyword arguments
        cell - An epithelial cell to update.
        """

        neighbours = Worldspace.getMooreNeighbours(self.world, cell.location, EpithelialStates.HEALTHY)

        for eCell in neighbours:
            if(eCell.canInfect):             
                chance = float((1 / EpithelialSystem.MAX_NEIGHBOURS) * (EpithelialCell.INFECT_RATE / ImmuneSystem.FLOW_RATE))
                if RNG.random() >= (1.0 - chance):
                    EpithelialSystem.setNextState(eCell, EpithelialStates.CONTAINING)
                    eCell.canInfect = False
                    eCell.focusId = cell.focusId
          
    def update(self):
        """The update method is responsible for operating on the epithelial cells, and changing their states."""

        #Update phase
        for cell in self.cells:

            #Age Death Step
            if cell.State != EpithelialStates.NATURAL_DEATH and cell.State != EpithelialStates.INFECTION_DEATH:
                if self.__updateAge(cell) == True:
                    continue

            #Cell Regeneration Step
            else:
                if self.__updateRegeneration(cell) == True:
                    continue                    
                    
            #Infection Progression Step
            if cell.State == EpithelialStates.CONTAINING or cell.State == EpithelialStates.EXPRESSING or cell.State == EpithelialStates.INFECTIOUS:

                #Infection time substep
                if self.__updateInfectionTime(cell) == True:
                    continue

                #Infection advancement substep
                self.__updateInfectionSeverity(cell)

                #Infection attempt substep
                if cell.State == EpithelialStates.INFECTIOUS:
                    self.__updateAttemptInfect(cell)

    def synchronise(self):
        """Sets the state of the epithelial cells for next iteration. Updates the internal count of immune cell states."""
        for cell in self.cells:
            if cell.State != cell.nextState:
                if cell.State == EpithelialStates.HEALTHY:
                    self.healthyCount -= 1
                elif cell.State == EpithelialStates.NATURAL_DEATH:
                    self.naturalDeathCount -= 1
                elif cell.State == EpithelialStates.INFECTION_DEATH:
                    self.infectionDeathCount -= 1
                elif cell.State == EpithelialStates.CONTAINING:
                    self.containingCount -= 1
                elif cell.State == EpithelialStates.EXPRESSING:
                    self.expressingCount -= 1
                elif cell.State == EpithelialStates.INFECTIOUS:
                    self.infectiousCount -= 1

                if cell.nextState == EpithelialStates.HEALTHY:
                    self.healthyCount += 1
                    if FocusSystem.ENABLED and cell.focusId != None:
                        self.fSys.removeCellFromFocus(cell)

                elif cell.nextState == EpithelialStates.NATURAL_DEATH:
                    self.naturalDeathCount += 1

                elif cell.nextState == EpithelialStates.INFECTION_DEATH:
                    self.infectionDeathCount += 1
                    if FocusSystem.ENABLED:
                        self.fSys.addCellToFocus(cell)

                elif cell.nextState == EpithelialStates.CONTAINING:
                    self.containingCount += 1

                elif cell.nextState == EpithelialStates.EXPRESSING:
                    self.expressingCount += 1

                elif cell.nextState == EpithelialStates.INFECTIOUS:
                    self.infectiousCount += 1

            cell.State = cell.nextState

        self.avgFociArea = self.infectionDeathCount / self.initialInfected
        if FocusSystem.ENABLED:
            self.fSys.update()

    @staticmethod
    def setNextState(cell, state):
        """Sets the state of an epithelial cell to a specific state. The state transition affects variable.
        
        Keyword arguments:
        cell -- EpithelialCell to change the state of
        state -- EpithelialState to change cell to
        """

        #Essentially a switch statement
        if state == EpithelialStates.INFECTION_DEATH or state == EpithelialStates.NATURAL_DEATH:
            cell.age       = 0
            cell.delay     = 0

        elif state == EpithelialStates.HEALTHY:
            cell.age          = 0
            cell.delay        = 0
            cell.timeInfected = 0
            cell.canInfect    = True
            cell.focusId      = None

        elif state == EpithelialStates.CONTAINING:
            cell.delay     = 0

        elif state == EpithelialStates.EXPRESSING:
            cell.delay     = 0

        cell.nextState = state

    @staticmethod
    def Configure(settings):
        """Static method. Should only be called once on startup. Sets the static const values of the EpithelialSystem class.

        Keyword arguments:
        settings -- ConfigSettings instance that contains values read from the config.ini file.
        """

        EpithelialSystem.INFECT_INIT = settings["fInfectInit"]
        EpithelialSystem.REGEN_ENABLED = settings["bRegenEnabled"]
        EpithelialSystem.RANDOM_AGE = settings["bRandomAge"]

class ImmuneSystem(ISystem):
    """The Immune System controls the movements and behaviour of the immune cells."""

    RECRUITMENT_DELAY = RECRUITMENT = ISENABLED = BASE_IMM_CELL = None
    INIT_CELLS = 0
    FLOW_RATE = 6.0 # TODO: Dynamic flow rate

    def __init__(self, world):
        """Constructor for ImmuneSystem

        Keyword arguments
        world -- 2d array of Worldsites
        """
        ISystem.__init__(self, world)

        self.virginCount        = 0
        self.matureCount        = 0
        self.recruitmentTimes   = []
        self.currentRecruitment = 0.0

        ImmuneSystem.INIT_CELLS = int((Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT) * ImmuneSystem.BASE_IMM_CELL) if int((Worldspace.GRID_WIDTH * Worldspace.GRID_HEIGHT) * ImmuneSystem.BASE_IMM_CELL) > 1 else 1

    def initialise(self):
        """Create the initial density of virgin cells in the worldspace, and add them to the system's cell list."""

        for i in range(ImmuneSystem.INIT_CELLS):
            x = RNG.randint(0, Worldspace.GRID_WIDTH - 1)
            y = RNG.randint(0, Worldspace.GRID_HEIGHT - 1)

            cell = ImmuneCell(Vector2d(x, y))
            cell.age = RNG.randint(0, ImmuneCell.IMM_LIFESPAN)
            self.cells.append(cell)
            self.world[x][y].getImmCells().append(cell)
            self.virginCount += 1

    def __updateAge(self, cell):
        """Private method, should only be called from public update() method. Updates an immune cell's age, and updates state if necessary.
        
        Keyword arguments
        cell - An immune cell to update.

        Returns true if rest of update step can be skipped over.
        """

        cell.age += 1

        if cell.age >= ImmuneCell.IMM_LIFESPAN:
            ImmuneSystem.setNextState(cell, ImmuneStates.DEAD)

            if cell.State == ImmuneStates.VIRGIN:
                self.virginCount -= 1
            else:
                self.matureCount -= 1

            return True
        return False

    def __updateMovement(self, cell):
        """Private method, should only be called from public update() method. Moves an immune cell to a random adjacent Worldsite.
        
        Keyword arguments
        cell - An immune cell to update.

        Returns Worldsite object that the immune cell has moved to.
        """

        site = self.world[cell.location.x][cell.location.y]
        site.getImmCells().remove(cell)

        x = 0
        y = 0

        while x == 0 and y == 0 :
            x = RNG.randint(-1,1)
            y = RNG.randint(-1,1)

        if(Worldspace.ISTOROIDAL):
            #Toroidal correction
            if cell.location.x + x < 0:
                x = Worldspace.GRID_WIDTH - 1
            elif cell.location.x + x > Worldspace.GRID_WIDTH - 1:
                x = -(Worldspace.GRID_WIDTH - 1)

            if cell.location.y + y < 0:
                y = Worldspace.GRID_HEIGHT - 1
            elif cell.location.y + y > Worldspace.GRID_HEIGHT - 1:
                y = -(Worldspace.GRID_HEIGHT - 1)

            cell.location.x = cell.location.x + x
            cell.location.y =  cell.location.y + y

        else:
            if cell.location.x + x < 0:
                x = 0
            elif cell.location.x + x > Worldspace.GRID_WIDTH - 1:
                x = 0

            if cell.location.y + y < 0:
                y = 0
            elif cell.location.y + y > Worldspace.GRID_HEIGHT - 1:
                y = 0

            cell.location.x = cell.location.x + x
            cell.location.y = cell.location.y + y


        site = self.world[cell.location.x][cell.location.y]
        site.getImmCells().append(cell)

        return site

    def __updateEncounter(self, cell, site):
        """Private method, should only be called from public update() method. Updates the state of an immune based on whether it has encountered a recognisable infection.
        
        Keyword arguments
        cell - An immune cell to update.
        site - Worldsite that the cell argument occupies.
        """

        if site.getECell().State == EpithelialStates.EXPRESSING or site.getECell().State == EpithelialStates.INFECTIOUS:
            if cell.State == ImmuneStates.VIRGIN:
                ImmuneSystem.setNextState(cell, ImmuneStates.MATURE)
                self.virginCount -= 1
                self.matureCount += 1

            EpithelialSystem.setNextState(site.getECell(), EpithelialStates.NATURAL_DEATH)

            self.recruitmentTimes.append(0)
    
    def __updateRecruitment(self):
        """Private method, should only be called from public update() method. Creates new immune cells randomly about the Worldspace as required."""

        cell = None

        for i in xrange(len(self.recruitmentTimes)-1,-1,-1):
            self.recruitmentTimes[i] += 1

            if self.recruitmentTimes[i] >= ImmuneSystem.RECRUITMENT_DELAY:
                del self.recruitmentTimes[i]

                self.currentRecruitment += ImmuneSystem.RECRUITMENT

                if self.currentRecruitment >= 1:
                    self.currentRecruitment -= 1

                    x = RNG.randint(0, Worldspace.GRID_WIDTH - 1)
                    y = RNG.randint(0, Worldspace.GRID_HEIGHT - 1)

                    cell = ImmuneCell(Vector2d(x, y))
                    ImmuneSystem.setNextState(cell, ImmuneStates.MATURE)
                    self.matureCount += 1
                    self.world[x][y].getImmCells().append(cell)
                    self.cells.append(cell)

    def __updateMaintenance(self):
        """Private method, should only be called from public update() method. Creates new virgin immune cells to maintain minimum density as required."""

        cell = None

        while self.virginCount < self.INIT_CELLS:
            x = RNG.randint(0, Worldspace.GRID_WIDTH - 1)
            y = RNG.randint(0, Worldspace.GRID_HEIGHT - 1)

            cell = ImmuneCell(Vector2d(x, y))
            self.world[x][y].getImmCells().append(cell)
            self.cells.append(cell)

            self.virginCount += 1

    def update(self):
        """Updates the immune cells, changing their states and moving them around."""

        site = None 

        #Update phase
        for cell in self.cells:

            #Age step
            if self.__updateAge(cell) == True:
                continue

            #Movement Step
            site = self.__updateMovement(cell)
            
            #Encounter Step
            self.__updateEncounter(cell, site)

        #Recruitment Phase
        self.__updateRecruitment()

        #Maintenance phase
        self.__updateMaintenance()

    def synchronise(self):
        """Sets the states of the cells for the next iteration."""

        for i in xrange(len(self.cells)-1,-1,-1):
            if self.cells[i].nextState == ImmuneStates.DEAD:
                site = self.world[self.cells[i].location.x][self.cells[i].location.y]
                site.getImmCells().remove(self.cells[i])
                del self.cells[i]
            else:
                self.cells[i].State = self.cells[i].nextState
                
    @staticmethod
    def setNextState(cell, state):
        """Sets up the next state of an immune cell for the next iteration."""

        if state == ImmuneStates.MATURE:
            cell.nextState = ImmuneStates.MATURE
        elif state == ImmuneStates.DEAD:
            cell.nextState = ImmuneStates.DEAD

    @staticmethod
    def Configure(settings):
        """Static method. Should only be called once on startup. Sets the static const values of the ImmuneSystem class.
        
        Keyword arguments:
        settings -- ConfigSettings instance that contains values read from the config.ini file.
        """

        ImmuneSystem.BASE_IMM_CELL = settings["fBaseImmCell"]
        ImmuneSystem.RECRUITMENT = settings["fRecruitment"]
        ImmuneSystem.RECRUITMENT_DELAY = settings["iRecruitDelay"]
        ImmuneSystem.ISENABLED = settings["bIsEnabled"]

class FocusSystem():
    """The Focus System updates the foci present in the simulation, deals with collision detection, and determines merged foci. """

    ENABLED = COLLISION_MERGE_PERCENTAGE = DEBUG_TEXT_ENABLED = None

    def __init__(self, world):
        """Constructor for FocusSystem

        Keyword arguments
        world -- 2d array of Worldsites
        """
        self.foci = {}
        self.nextId = 0
        self.world = world
        self.mergeDetected = []

    def addNewFocus(self, origin):
        """Add new focus to the focus system at a particular cell.

        Keyword arguments
        origin -- Origin epithelial cell of the focus. 
        """
        origin.focusId = self.nextId
        focus = Worldspace.Focus(origin, self.nextId)
        self.foci.update({self.nextId: focus})
        self.nextId += 1
        
    def addCellToFocus(self, cell):
        """Adds cell to a focus, determined by the cell's focus id.

        Keyword arguments
        cell -- Epithelial cell to add to a focus.
        """
        focus = self.foci.get(cell.focusId)
        focus.perimeter.append(cell)
        focus.cellCount += 1

    def removeCellFromFocus(self, cell):
        """Remove cell from focus and adds any new uncovered perimeter cells in.

        Keyword arguments
        cell -- Epithelial cell to remove from a focus.
        """
        focus = self.foci.get(cell.focusId)
        for x in xrange(focus.perimeter-1, -1, -1):
            if focus.perimeter[x] == cell:
                del focus.perimeter[x]
                break
        focus.cellCount -= 1

        self.__discoverNewPerimeterCellsByLocation(cell.location)
        
    def update(self):
        """Updates the focus system. Calls private updating methods."""

        self.__updatePerimeterCells()
        self.__updateCollisions()
        #self.__debugPrint()

    def __discoverNewPerimeterCellsByLocation(self, location, focus):
        """Gets new perimeter cells based on neighbours of cell at given location.
        
        Keyword arguments
        location -- Vector2d instance representing location of a cell
        focus    -- Focus instance to discover perimeter for
        """
        neighbours = Worldspace.getMooreNeighbours(self.world, location, EpithelialStates.INFECTION_DEATH)
        for neighbour in neighbours:
            if neighbour.focusId != focus.Id:
                if not (neighbour in focus.perimeter):
                    focus.perimeter.append(neighbour)


    def __updatePerimeterCells(self):
        """This is a private method, and should only be called from the public update() method. Updates the bounding structure of each focus."""

        for focus in self.foci.values():
            for i in xrange(len(focus.perimeter)-1,-1,-1):
                perimeterCell = focus.perimeter[i]
                infectionDeathCount = Worldspace.getMooreNeighbourStateCount(self.world, perimeterCell.location, EpithelialStates.INFECTION_DEATH)
                #naturalDeathCount = Worldspace.getMooreNeighbourStateCount(self.world, perimeterCell.location, EpithelialStates.NATURAL_DEATH)
                #sum = infectionDeathCount + naturalDeathCount
                if infectionDeathCount == EpithelialSystem.MAX_NEIGHBOURS:
                    del focus.perimeter[i]

    def __updateCollisions(self):
        """This is a private method, and should only be called from the public update() method. Discovers collisions and determines merges."""

        for focus in self.foci.values():
            if focus.isEnabled:
                collisions = {}
                for i in xrange(len(focus.perimeter)):
                    perimeterCell = focus.perimeter[i]
                    perimeterNeighbours = Worldspace.getMooreNeighbours(self.world, perimeterCell.location, EpithelialStates.INFECTION_DEATH)
                    for neighbour in perimeterNeighbours:
                        if neighbour.focusId != perimeterCell.focusId:
                            if collisions.has_key(neighbour.focusId):
                                if not (neighbour.location in collisions[neighbour.focusId]):
                                    collisions[neighbour.focusId].append(neighbour.location)
                                else:
                                    continue
                            else:
                                collisions[neighbour.focusId] = [neighbour.location]

                for collisionList in collisions.values():
                    collisionCount = len(collisionList)

                    if collisionCount > (len(focus.perimeter) * (FocusSystem.COLLISION_MERGE_PERCENTAGE / 100.0) if len(focus.perimeter) * (FocusSystem.COLLISION_MERGE_PERCENTAGE / 100.0) > 1 else 1):
                    
                        focus.isEnabled = False
                        if FocusSystem.DEBUG_TEXT_ENABLED:
                            Log.out("Merge detected on Focus #%s" % focus.id)
                        self.mergeDetected.append(focus)
                    
    # TODO: Remove this in final version.
    def __debugPrint(self):
        """Debug method, to be removed. Prints the focus by id and it's area."""
        for focus in self.foci.values():
            if focus.isEnabled:
                Log.out("Focus #%s: %s" % (focus.id , focus.cellCount))

    @staticmethod
    def Configure(settings):
        """Static method. Should only be called once on startup. Sets the static const values of the FocusSystem class.

        Keyword arguments:
        settings -- ConfigSettings instance that contains values read from the config.ini file.
        """

        FocusSystem.ENABLED                    = settings["bIsEnabled"]
        FocusSystem.COLLISION_MERGE_PERCENTAGE = settings["iCollisionsForMergePercentage"] if settings["iCollisionsForMergePercentage"] > 0 else 1
        FocusSystem.DEBUG_TEXT_ENABLED         = settings["bDebugTextEnabled"]