from Tkinter import Tk, Canvas, PhotoImage
from PIL import Image, ImageDraw, ImageFont

from Cells import EpithelialCell, ImmuneCell, EpithelialStates, ImmuneStates
from Worldspace import Worldsite, Vector2d

import SimUtils

TIME_TEXT_PREFIX = "Time Elapsed: "
IMAGES_DIR_NAME = "images/"
TEMP_DIR_NAME = "temp/"
SIM_RUN_DIR_PREFIX = "run"
IMAGE_NAME_PREFIX = "sim_vis_frame"
IMAGE_EXTENSION = ".jpg"
TEMP_IMAGE_EXTENSION = ".PGM"

CANVAS_TEXT_PADDING = 40
CANVAS_TEXT_SIZE = 14

class SimVis(object):
    """Defines the visualisation aspects of the program. Draws and updates all visuals."""

    SNAPSHOT_ENABLED = ENABLED = DEBUG_ID_ENABLED = HIGHLIGHT_COLLISIONS = SQUARESIZE = SNAPSHOT_HEIGHT = SNAPSHOT_WIDTH = None

    def __init__(self, width, height, squareSize):

        self.simRootPath = ""
        self.setSimRootPath(SimUtils.getRootPath())
        self.currentFolder = self.simRootPath
        self.simRun = 0;
        self.simRunFolder = ""
        self.__initImageFolder()
        self.__updateSimRunFolder()

        self.width = width
        self.height = height

        self.root = Tk()
        self.squareSize = squareSize
        self.CANVAS_WIDTH = (self.width * squareSize)
        self.CANVAS_HEIGHT = (self.height * squareSize) + CANVAS_TEXT_PADDING

        self.canvas = Canvas(self.root, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg='white')
        self.canvas.pack()

        self.timeFont = ImageFont.truetype("Arialbd.ttf", CANVAS_TEXT_SIZE)
        self.time = 0.0
        self.timeMeasurement = "timesteps"
        self.timeStepsInMeasurement = 1
        self.timeText = None
        self.__updateTimeText()

        self.root.minsize(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        self.root.geometry(str(self.CANVAS_WIDTH)+"x"+str(self.CANVAS_HEIGHT))

        self.world = None

        self.white = (255, 255, 255)
        # PIL image can be saved as .png .jpg .gif or .bmp file (among others)
        self.filenameJPG = None
        self.filename = None
        # PIL create an empty image and draw object to draw on
        # memory only, not visible
        self.image = Image.new("RGB", (self.CANVAS_WIDTH, self.CANVAS_HEIGHT), self.white)
        self.draw = ImageDraw.Draw(self.image)

    def __updateSimRunFolder(self) :
        if self.simRun > 0 :
            self.simRunFolder = SIM_RUN_DIR_PREFIX + str(self.simRun) + "/"
        else :
            self.simRunFolder = ""

        imageFolder = self.__getImageFolder()
        SimUtils.initFolder(folderName=imageFolder)

    def __updateTimeText(self) :
        self.timeText = TIME_TEXT_PREFIX + str(self.time) + " " + self.timeMeasurement

    def setTimeStepsInMeasurement(self, val):
        self.timeStepsInMeasurement = val
        self.__updateTimeText()

    def setTimeMeasurement(self, measurement):
        self.timeMeasurement = measurement
        self.__updateTimeText()

    def init(self, world, run=0) :
        self.canvas.delete("all")
        self.world = world
        self.setSimRun(run)

    def display(self):
        self.root.mainloop() # this method will hang until you close the TK (window), but is essential to display the window and canvas

    # Draw a 10 X 10 sqaure on the canvas with no border
    def drawSquare(self, x, y, color):
        if self.world[x][y].drawColor == color :
            return
        self.world[x][y].drawColor = color

        xPos = x * self.squareSize
        yPos = y * self.squareSize

        self.draw.rectangle([xPos , yPos, xPos + self.squareSize - 1, yPos + self.squareSize - 1], fill=color)

    # TODO: Remove this in final version?
    def __focusDebugDraw(self, x, y, id, colour):
        self.draw.text((x, y), str(id), fill=colour)

    #Draw an Epithelial Cell, the colour is set depandant on its state     
    def drawEpiCell(self, eCell):
        x = eCell.location.x
        y = eCell.location.y

        color = None

        if(eCell.State == EpithelialStates.HEALTHY) :
            color = "#FCFEF5"

        elif(eCell.State == EpithelialStates.CONTAINING):
            color = "#F9D423"

        elif(eCell.State == EpithelialStates.EXPRESSING):
            color = "#FC913A"

        elif(eCell.State == EpithelialStates.INFECTIOUS):
            color = "#C21A01"

        elif(eCell.State == EpithelialStates.NATURAL_DEATH or eCell.State == EpithelialStates.INFECTION_DEATH):
            color = "#000000"
        else:
             raise AttributeError('Illegal Epithelial Cell State')

        self.drawSquare(x, y, color)

        # TODO: Remove this in final version?
        if SimVis.DEBUG_ID_ENABLED:
            if eCell.focusId != None:
                if eCell.State == EpithelialStates.INFECTION_DEATH:
                    self.__focusDebugDraw(x * self.squareSize, y * self.squareSize, eCell.focusId, "#FFFFFF")
                else:
                    self.__focusDebugDraw(x * self.squareSize, y * self.squareSize, eCell.focusId, "#000000")
            
    def drawSimWorld(self, save, timesteps):
        if self.width == 0 and self.height == 0 :
            return

        #self.image = Image.new("RGB", (self.CANVAS_WIDTH, self.CANVAS_HEIGHT), self.white)
        #self.draw = ImageDraw.Draw(self.image)

        for x in xrange(0, self.width) :
            for y in xrange(0, self.height) :
                site = self.world[x][y]

                drawImmCell = False
                immCells = site.getImmCells()
                if len(immCells) > 0 :
                    mature = False
                    for immCell in immCells :
                        if immCell.State == ImmuneStates.MATURE :
                            self.drawImmCell(immCell)
                            drawImmCell = True
                            mature = True
                            break
                    if mature == False :
                        self.drawImmCell(immCell)
                        drawImmCell = True


                if drawImmCell == False :
                    eCell = site.getECell()
                    self.drawEpiCell(eCell)

        self.time = round(timesteps / self.timeStepsInMeasurement, 1)
        self.__updateTimeText()

        w, h = self.draw.textsize(self.timeText, self.timeFont)
        x = (self.CANVAS_WIDTH / 2) - (w/2)
        y = (self.CANVAS_HEIGHT - (CANVAS_TEXT_PADDING/2) - (h/2))
        self.draw.text((x, y), self.timeText, (0,0,0), font=self.timeFont)

        self.__savePILImageToFile(save)
        self.__updateCanvas(save)

        self.draw.rectangle([0, self.CANVAS_HEIGHT - CANVAS_TEXT_PADDING, 
                             self.CANVAS_WIDTH, self.CANVAS_HEIGHT], fill="white")

        #del self.draw
        #del self.image

    def drawImmCell(self, immCell):

        x = immCell.location.x
        y = immCell.location.y

        color = None

        if(immCell.State == ImmuneStates.VIRGIN) :
            color = "#C0D860"

        elif(immCell.State == ImmuneStates.MATURE):
            color = "#789048"

        else:
            raise AttributeError('Illegal Immune Cell State')

        self.drawSquare(x, y, color)

    def drawCollision(self, cell):
        self.drawSquare(cell.location.x, cell.location.y, "#5078F0")
        if SimVis.DEBUG_ID_ENABLED:
            self.__focusDebugDraw(cell.location.x * self.squareSize, cell.location.y * self.squareSize, str(cell.focusId), "#000000")

    def __initImageFolder(self):
        SimUtils.initFolder(folderParent=self.simRootPath, folderName=IMAGES_DIR_NAME, overwrite=True)
        SimUtils.initFolderPath(folderPath=self.__getTempFolder(), overwrite=True)

    def __getImageFolder(self):
        return self.simRootPath + IMAGES_DIR_NAME + self.simRunFolder

    def __getTempFolder(self):
        return self.simRootPath + IMAGES_DIR_NAME + TEMP_DIR_NAME

    def __savePILImageToFile(self, save):
        imageFolder = self.__getImageFolder()
        tempFolder = self.__getTempFolder()

        if save :
            self.filenameJPG = imageFolder + self.__getImageFileName()
            self.image.save(self.filenameJPG)
            
        self.filename = tempFolder + IMAGE_NAME_PREFIX + TEMP_IMAGE_EXTENSION
        self.image.save(self.filename)

    def __getImageFileName(self) :
        return IMAGE_NAME_PREFIX + "_" + str(int(self.time)) + self.timeMeasurement + "_" + str(self.height) + "x" + str(self.width) + IMAGE_EXTENSION

    def __updateCanvas(self, save):
        # draw PIL image to tkinter canvas
        self.canvas.background = PhotoImage(file=self.filename)
        self.canvas.create_image(2, 2, image=self.canvas.background, anchor="nw")

        self.canvas.update()

    def setSimRootPath(self, folderPath):
        if folderPath == "" :
            folderPath = "."
        if folderPath[len(folderPath) - 1] != '/' :
            folderPath += '/'
        self.simPathFolder = folderPath

    def setSimRun(self, run):
        self.simRun = run;
        self.__updateSimRunFolder();

    @staticmethod
    def Configure(settings):
        SimVis.ENABLED              = settings["bIsEnabled"]
        SimVis.SNAPSHOT_ENABLED     = settings["bSnapshotEnabled"]
        SimVis.SNAPSHOT_HEIGHT      = settings["iSnapshotHeight"]
        SimVis.SNAPSHOT_WIDTH       = settings["iSnapshotWidth"]
        SimVis.SQUARESIZE           = settings["iSquareSize"]
        SimVis.DEBUG_ID_ENABLED     = settings["bDebugFocusIdEnabled"]
        SimVis.HIGHLIGHT_COLLISIONS = settings["bHighlightCollisions"]
