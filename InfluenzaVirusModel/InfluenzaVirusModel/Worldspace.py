ISTOROIDAL = GRID_HEIGHT = GRID_WIDTH = None

def Configure(settings):
    """Set the constant configuration values of the worldspace.

    Keyword arguments:
    settings -- The ConfigSettings instance that contains configurations.
    """
    global ISTOROIDAL
    global GRID_WIDTH
    global GRID_HEIGHT
    ISTOROIDAL = settings["bIsToroidal"]
    GRID_WIDTH = settings["iGridWidth"]
    GRID_HEIGHT = settings["iGridHeight"]
    
class Worldsite:
    """Class that represents an x, y location in the worldspace. Contains all entities currently in location represented."""

    def __init__(self, location):
        """Create a new site at given location
           
        Keyword arguments:
        location -- The (x, y) coordinate of the new site in the worldspace.        
        """
        self.location = location
        self.immCells = []
        self.eCell = None
        self.visual = None
        self.drawColor = None
   
    def getLocation(self):
        """Get the (x, y) coordinate of the site.
        
        Returns vector2d.
        """
        return self.location

    def getECell(self):
        """Get the epithelial cell at this site.
        
        Returns eCell.
        """
        return self.eCell

    def getImmCells(self):
        """Get the list of immune cells currently at this site.
        
        Returns list of immCell.
        """
        return self.immCells

class Vector2d:
    """Class that contains the x, y coordinates of a cell in the worldspace."""

    def __init__(self, x, y):
        """Create new vector2d.
        
        Keyword arguments:
        x -- x coordinate in the worldspace
        y -- y coorindate in the worldspace
        """
        self.x = x
        self.y = y

class Focus:
    """Class that acts as a container of areas of dead cells."""

    def __init__(self, origin, id):
        """Constructor for focus.

        Keyword arguments:
        origin -- Epithelial cell that is the original infected cell of this focus.
        id -- Unique int id of this focus.
        """

        self.origin    = origin
        self.perimeter = []
        self.cellCount = 0
        self.isEnabled = True
        self.id        = id

def getMooreNeighbourStateCount(world, location, state):
        """Parses through the adjacent sites in the toroidal world, returns number of Moore neighbours that possess the given state.
        
        Keyword arguments:
        location -- Vector2d, (x, y) coordinate of site to get Moore neighbour states for.
        state -- EpithelialState to check for.
        """
        x = location.x
        y = location.y

        neighbour = 0

        if ISTOROIDAL:
            if world[x-1 if x-1 > -1 else GRID_WIDTH-1][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell().State == state:
                neighbour += 1

            if world[x-1 if x-1 > -1 else GRID_WIDTH-1][y].getECell().State == state:
                neighbour += 1

            if world[x-1 if x-1 > -1 else GRID_WIDTH-1][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell().State == state:
                neighbour += 1

            if world[x][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell().State == state:
                neighbour += 1

            if world[x][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell().State == state:
                neighbour += 1

            if world[x+1 if x+1 < GRID_WIDTH-1 else 0][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell().State == state:
                neighbour += 1

            if world[x+1 if x+1 < GRID_WIDTH-1 else 0][y].getECell().State == state:
                neighbour += 1

            if world[x+1 if x+1 < GRID_WIDTH-1 else 0][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell().State == state:
                neighbour += 1
        else:
            if x-1 >= 0 and y-1 >= 0 and world[x-1][y-1].getECell().State == state:
                neighbour += 1

            if x-1 >= 0 and world[x-1][y].getECell().State == state:
                neighbour += 1

            if x-1 >= 0 and y+1 <= GRID_HEIGHT-1 and world[x-1][y+1].getECell().State == state:
                neighbour += 1

            if y-1 >= 0 and world[x][y-1].getECell().State == state:
                neighbour += 1

            if y+1 <= GRID_HEIGHT-1 and world[x][y+1].getECell().State == state:
                neighbour += 1

            if x+1 <= GRID_WIDTH-1 and y-1 >=0 and world[x+1][y-1].getECell().State == state:
                neighbour += 1

            if x+1 <= GRID_WIDTH-1 and world[x+1][y].getECell().State == state:
                neighbour += 1

            if x+1 <= GRID_WIDTH-1 and y+1 <= GRID_HEIGHT-1 and world[x+1][y+1].getECell().State == state:
                neighbour += 1

        return neighbour

def getMooreNeighbours(world, location, state = None):
    """Parses through the adjacent sites in the toroidal world, returns list of Moore neighbours that possess the given state.
        
    Keyword arguments:
    location -- Vector2d, (x, y) coordinate of site to get Moore neighbour states for.
    state -- EpithelialState to check for.
    """
    x = location.x
    y = location.y

    neighbours = []

    if ISTOROIDAL:
        if world[x-1 if x-1 > -1 else GRID_WIDTH-1][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell().State == state or state == None:
            neighbours.append(world[x-1 if x-1 > -1 else GRID_WIDTH-1][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell())

        if world[x-1 if x-1 > -1 else GRID_WIDTH-1][y].getECell().State == state or state == None:
            neighbours.append(world[x-1 if x-1 > -1 else GRID_WIDTH-1][y].getECell())

        if world[x-1 if x-1 > -1 else GRID_WIDTH-1][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell().State == state or state == None:
            neighbours.append(world[x-1 if x-1 > -1 else GRID_WIDTH-1][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell())

        if world[x][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell().State == state or state == None:
            neighbours.append(world[x][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell())

        if world[x][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell().State == state or state == None:
            neighbours.append(world[x][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell())

        if world[x+1 if x+1 < GRID_WIDTH-1 else 0][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell().State == state or state == None:
            neighbours.append(world[x+1 if x+1 < GRID_WIDTH-1 else 0][y-1 if y-1>-1 else GRID_HEIGHT-1].getECell())

        if world[x+1 if x+1 < GRID_WIDTH-1 else 0][y].getECell().State == state or state == None:
            neighbours.append(world[x+1 if x+1 < GRID_WIDTH-1 else 0][y].getECell())

        if world[x+1 if x+1 < GRID_WIDTH-1 else 0][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell().State == state or state == None:
            neighbours.append(world[x+1 if x+1 < GRID_WIDTH-1 else 0][y+1 if y+1<GRID_HEIGHT-1 else 0].getECell())
    else:
        if x-1 >= 0 and y-1 >= 0 and world[x-1][y-1].getECell().State == state or state == None:
            neighbours.append(world[x-1][y-1].getECell())

        if x-1 >= 0 and world[x-1][y].getECell().State == state or state == None:
            neighbours.append(world[x-1][y].getECell())

        if x-1 >= 0 and y+1 <= GRID_HEIGHT-1 and world[x-1][y+1].getECell().State == state or state == None:
            neighbours.append(world[x-1][y+1].getECell())

        if y-1 >= 0 and world[x][y-1].getECell().State == state or state == None:
            neighbours.append(world[x][y-1].getECell())

        if y+1 <= GRID_HEIGHT-1 and world[x][y+1].getECell().State == state or state == None:
            neighbours.append(world[x][y+1].getECell())

        if x+1 <= GRID_WIDTH-1 and y-1 >=0 and world[x+1][y-1].getECell().State == state or state == None:
            neighbours.append(world[x+1][y-1].getECell())

        if x+1 <= GRID_WIDTH-1 and world[x+1][y].getECell().State == state or state == None:
            neighbours.append(world[x+1][y].getECell())

        if x+1 <= GRID_WIDTH-1 and y+1 <= GRID_HEIGHT-1 and world[x+1][y+1].getECell().State == state or state == None:
            neighbours.append(world[x+1][y+1].getECell())
    
    return neighbours