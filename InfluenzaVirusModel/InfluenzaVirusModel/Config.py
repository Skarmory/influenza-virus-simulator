import ConfigParser
import os
import Worldspace
import Systems
import Cells
import Program
import Systems
import SimulationVisualization
import Graph
from Logger import StdOutLogger as Log

class ConfigReader(object):
    """The ConfigReader parses the config file and returns the values. Additionally, it also reconstructs the config file if it is deleted or corrupted."""

    def __init__(self):
        """Constructor for ConfigReader"""

        self.configParser = ConfigParser.ConfigParser()
        self.configParser.optionxform = str
        self.configSettings = dict()
        self.reconstruct = False
    
    def SetConfiguration(self):
        """Reads the values from the config.ini file into a dictionary and returns it.
        
        Returns dict() <str, dyanmic>
        """

        try:
            self.configParser.read(os.getcwd() + "\\config.ini")
            sections = self.configParser.sections()

            if len(sections) == 0:
                self.__reconstruct()
                return self.SetConfiguration()

            for section in xrange(len(sections)):
                configSettings = dict()
                str = sections[section]
                if str == "World":
                    configSettings["bIsToroidal"] = self.configParser.getboolean(str, "bIsToroidal")
                    configSettings["iGridWidth"] = self.checkIntValBounds(str, "iGridWidth", 1)
                    configSettings["iGridHeight"] = self.checkIntValBounds(str, "iGridHeight", 1)
                    Worldspace.Configure(configSettings)
                elif str == "General":
                    self.configSettings["iNumberOfRuns"] = self.checkIntValBounds(str, "iNumberOfRuns", 1)
                    self.configSettings["iRunTime"] = self.checkIntValBounds(str, "iRunTime", 0)
                    self.configSettings["bDebugTextEnabled"] = self.configParser.getboolean(str, "bDebugTextEnabled")
                elif str == "Interface":
                    pass
                elif str == "ImmuneSystem":
                    configSettings["fBaseImmCell"] = self.checkFloatValBounds(str, "fBaseImmCell", 0)
                    configSettings["bIsEnabled"] = self.configParser.getboolean(str, "bIsEnabled")
                    configSettings["fRecruitment"] = self.checkFloatValBounds(str, "fRecruitment", 0)
                    configSettings["iRecruitDelay"] = self.checkIntValBounds(str, "iRecruitDelay", 0)
                    Systems.ImmuneSystem.Configure(configSettings)
                elif str == "EpithelialSystem":
                    configSettings["fInfectInit"] = self.checkFloatValBounds(str, "fInfectInit", 0)
                    configSettings["bRegenEnabled"] = self.configParser.getboolean(str, "bRegenEnabled")
                    configSettings["bRandomAge"] = self.configParser.getboolean(str, "bRandomAge")
                    Systems.EpithelialSystem.Configure(configSettings)
                elif str == "FocusSystem":
                    configSettings["bIsEnabled"] = self.configParser.getboolean(str, "bIsEnabled")
                    configSettings["iCollisionsForMergePercentage"] = self.checkIntValBounds(str, "iCollisionsForMergePercentage", 0, 100)
                    configSettings["bDebugTextEnabled"] = self.configParser.getboolean(str, "bDebugTextEnabled")
                    Systems.FocusSystem.Configure(configSettings)
                elif str == "ImmuneCell":
                    configSettings["iImmuneLifespan"] = self.checkIntValBounds(str, "iImmuneLifespan", 0)
                    Cells.ImmuneCell.Configure(configSettings)
                elif str == "EpithelialCell":
                    configSettings["iEpithelialLifespan"] = self.checkIntValBounds(str, "iEpithelialLifespan", 0)
                    configSettings["iDivisionTime"] = self.checkIntValBounds(str, "iDivisionTime", 0)
                    configSettings["iExpressDelay"] = self.checkIntValBounds(str, "iExpressDelay", 0)
                    configSettings["iInfectDelay"] = self.checkIntValBounds(str, "iInfectDelay", 0)
                    configSettings["iInfectLifespan"] = self.checkIntValBounds(str, "iInfectLifespan", 0)
                    configSettings["fInfectRate"] = self.checkFloatValBounds(str, "iInfectRate", 0)
                    Cells.EpithelialCell.Configure(configSettings)
                elif str == "SimulationVisualisation":
                    configSettings["bIsEnabled"] = self.configParser.getboolean(str, "bIsEnabled")
                    configSettings["bSnapshotEnabled"] = self.configParser.getboolean(str, "bSnapshotEnabled")
                    configSettings["iSnapshotHeight"] = self.checkIntValBounds(str, "iSnapshotHeight", 0)
                    configSettings["iSnapshotWidth"] = self.checkIntValBounds(str, "iSnapshotWidth", 0)
                    configSettings["iSquareSize"] = self.checkIntValBounds(str, "iSquareSize", 1)
                    configSettings["bDebugFocusIdEnabled"] = self.configParser.getboolean(str, "bDebugFocusIdEnabled")
                    configSettings["bHighlightCollisions"] = self.configParser.getboolean(str, "bHighlightCollisions") 
                    SimulationVisualization.SimVis.Configure(configSettings)
                elif str == "Graph":
                    configSettings["bShowGraphOnFinish"] = self.configParser.getboolean(str, "bShowGraphOnFinish")
                    Graph.Graph.Configure(configSettings)

                    

        except Exception as e:
            if self.reconstruct == False :
                Log.err("Error in config file: " + e.message)
                Log.err("Restoring to defaults...")
                self.__reconstruct()
                return self.SetConfiguration()
            else :
                raise Exception("Failed to reconstruct config.ini file")

        return self.configSettings

    def __reconstruct(self):
        """Private method, should only be called from SetConfiguration if the config.ini file requires rebuilding."""

        defaults = self.__createDefaults()
        for keys in self.configParser.sections():
            self.configParser.remove_section(keys)

        for x in xrange(len(defaults)):
            section = defaults[x]
            for sectionkey in section.keys():
                options = section[sectionkey]
                
                self.configParser.add_section(sectionkey)
                for option in options.keys():
                    self.configParser.set(sectionkey, option, options[option])

        with open(os.getcwd() + '\\config.ini', 'w') as f:
            self.configParser.write(f)

        self.reconstruct = True

    def __createDefaults(self):
        """Private method, should only be called by __reconstruct(). Generate a dict of <str, dict<str, str>>.
        
        Returns dict<str, dict<str, str>>
        """
        defaults = []

        defaults.append({"General": {"iNumberOfRuns":"1", "iRunTime":"1440", "bDebugTextEnabled":"True"}})
        defaults.append({"World": {"bIsToroidal":"True", "iGridWidth":"440", "iGridHeight":"280"}})
        defaults.append({"ImmuneSystem":{"bIsEnabled":"True", "iRecruitDelay":"7", "fBaseImmCell":"0.00015", "fRecruitment":"0.25"}})
        defaults.append({"EpithelialSystem":{"fInfectInit":"0.01", "bRegenEnabled":"True", "bRandomAge":"True"}})
        defaults.append({"FocusSystem":{"bIsEnabled":"False", "iCollisionsForMergePercentage":"10", "bDebugTextEnabled": "False"}})
        defaults.append({"EpithelialCell":{"iEpithelialLifespan":"2280","iInfectRate":"2","iInfectLifespan":"144","iExpressDelay":"24","iInfectDelay":"12","iDivisionTime":"72"}})
        defaults.append({"ImmuneCell":{"iImmuneLifespan":"1008"}})
        defaults.append({"SimulationVisualisation": {"bIsEnabled":"True", "bSnapshotEnabled":"True", "iSnapshotWidth":"100", "iSnapshotHeight":"100", "iSquareSize":"4", "bDebugFocusIdEnabled": "False", "bHighlightCollisions": "True"}})
        defaults.append({"Graph":{"bShowGraphOnFinish":"True"}})

        return defaults

    def checkIntValBounds(self, dictKey, valueString, lowerBound=None, upperBound=None) :
        val = self.configParser.getint(dictKey, valueString)
        if lowerBound != None :
            if val < lowerBound :
                val = self.getIntDefault(dictKey, valueString)
                Log.err("value of " + valueString + " must be >= " +  str(lowerBound) + ", using default instead = " + str(val))
        if upperBound != None :
            if val > upperBound :
                val = self.getIntDefault(dictKey, valueString)
                Log.err("value of " + valueString + " must be <= " +  str(upperBound) + ", using default instead = " + str(val))
        return val

    def checkFloatValBounds(self, dictKey, valueString, lowerBound=None, upperBound=None) :
        val = self.configParser.getfloat(dictKey, valueString)
        if lowerBound != None :
            if val < lowerBound :
                val = self.getFloatDefault(dictKey, valueString)
                Log.err("value of " + valueString + " must be >= " +  str(lowerBound) + ", using default instead = " + str(val))
        if upperBound != None :
            if val > upperBound :
                val = self.getFloatDefault(dictKey, valueString)
                Log.err("value of " + valueString + " must be <= " +  str(upperBound) + ", using default instead = " + str(val))
        return val

    def getValDefault(self, dictKey, valueString) :
        defaults = self.__createDefaults()
        dict = None
        if dictKey == "General" :
            dict = defaults[0]
        elif dictKey == "World" :
            dict = defaults[1]
        elif dictKey == "ImmuneSystem" :
            dict = defaults[2]
        elif dictKey == "EpithelialSystem" :
            dict = defaults[3]
        elif dictKey == "FocusSystem" :
            dict = defaults[4]
        elif dictKey == "EpithelialCell" :
            dict = defaults[5]
        elif dictKey == "ImmuneCell" :
            dict = defaults[6]
        elif dictKey == "SimulationVisualisation" :
            dict = defaults[7]
        elif dictKey == "Graph" :
            dict = defaults[8]
        if dict != None :
            return dict[dictKey][valueString]
        else :
            return dict

    def getIntDefault(self, dictKey, valueString) :
        return int(self.getValDefault(dictKey, valueString))

    def getFloatDefault(self, dictKey, valueString) :
        return float(self.getValDefault(dictKey, valueString))

    def getBoolDefault(self, dictKey, valueString) :
        return bool(self.getValDefault(dictKey, valueString))
