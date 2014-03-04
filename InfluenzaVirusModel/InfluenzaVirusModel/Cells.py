from abc import ABCMeta, abstractmethod

class ICell(object):
    """Cell interface, to be inherited by concrete classes."""

    __metaclass__ = ABCMeta

    def __init__(self, location):
        """Constructor for ICell.

        Keyword arguments:
        location -- Vector2D representing the (x, y) coordinate of the cell in the worldspace.
        """
        self.location = location
        self.age = 0

class EpithelialCell(ICell):
    """Epithlial cells are the targets of the virus. There is one epithelial cell per site in the worldspace, and they will go through various stages of infection."""

    INFECT_RATE = INFECT_LIFESPAN = EXPRESS_DELAY = INFECT_DELAY = DIVISION_TIME = CELL_LIFESPAN = None

    def __init__(self, location):
        """Constructor for EpithelialCell.

        Keyword arguments:
        location -- Vector2D representing the (x, y) coordinate of the cell in the worldspace.
        """
        ICell.__init__(self, location)

        self.State          = EpithelialStates.HEALTHY
        self.nextState      = EpithelialStates.HEALTHY 
        self.delay          = 0
        self.timeInfected   = 0
        self.focusId        = None
        self.canInfect      = True

    @staticmethod
    def Configure(settings):
        """Static method. Should only be called once on startup. Sets the static const values of the EpithelialCell class.
        
        Keyword arguments:
        settings -- ConfigSettings instance that contains values read from the config.ini file.
        """

        EpithelialCell.CELL_LIFESPAN = settings["iEpithelialLifespan"]
        EpithelialCell.INFECT_RATE = settings["fInfectRate"]
        EpithelialCell.INFECT_LIFESPAN = settings["iInfectLifespan"]
        EpithelialCell.EXPRESS_DELAY = settings["iExpressDelay"]
        EpithelialCell.INFECT_DELAY = settings["iInfectDelay"]
        EpithelialCell.DIVISION_TIME = settings["iDivisionTime"]

class ImmuneCell(ICell):
    """Epithlial cells are the targets of the virus. There is one epithelial cell per site in the worldspace, and they will go through various stages of infection."""

    IMM_LIFESPAN = None

    def __init__(self, location):
        """Constructor for ImmuneCell.

        Keyword arguments:
        location -- Vector2D representing the (x, y) coordinate of the cell in the worldspace.
        """
        ICell.__init__(self, location)

        self.State     = ImmuneStates.VIRGIN
        self.nextState = ImmuneStates.VIRGIN

    @staticmethod
    def Configure(settings):
        """Static method. Should only be called once on startup. Sets the static const values of the ImmuneCell class.
        
        Keyword arguments:
        settings -- ConfigSettings instance that contains values read from the config.ini file.
        """

        ImmuneCell.IMM_LIFESPAN = settings["iImmuneLifespan"]

def enum(**enums):
    """Definition of an enum because Python 2.7 doesn't support them easily."""
    return type("Enum", (), enums)

# The two state enums for both Epithelial cells and Immune cells.
EpithelialStates = enum(HEALTHY = 0, CONTAINING = 1, EXPRESSING = 2, INFECTIOUS = 3, INFECTION_DEATH = 4, NATURAL_DEATH = 5)
ImmuneStates     = enum(VIRGIN = 0, MATURE = 1, DEAD = 2)