import shutil
import os
import sys

def initFolder(folderParent=None, folderName=None, overwrite=False) :
    if folderName == None :
        raise AttributeError("folderName must not be null!")
    if folderParent == None :
        folderParent = getRootPath()

    nameLength = len(folderName)
    rootLength = len(folderParent)

    if nameLength > 0 :
        if folderName[nameLength - 1] != '/' :
            folderName += '/'

    if rootLength > 0 :
        if folderParent[rootLength - 1] != '/' :
            folderParent += '/'

    path = folderParent + folderName
    initFolderPath(path, overwrite)

def initFolderPath(folderPath=None, overwrite=False) :
    if folderPath == None :
        raise AttributeError("folderPath must not be null!")

    if overwrite :
        if os.path.exists(folderPath) :
            shutil.rmtree(folderPath) # clear folder
        os.makedirs(folderPath)
    else :
        if os.path.exists(folderPath) == False :
            os.makedirs(folderPath)

def getRootPath() :
    return os.path.dirname(sys.argv[0])