import os
import json
import pathlib
import text_preprocessing as tp

def importJSON():

    try:
        if not (os.getcwd().endswith("JSONFiles")):
            checkJSONDir = os.path.join(pathlib.Path(__file__).parent.parent, 'JSONFiles')
            if not (os.path.exists(checkJSONDir)):
                os.mkdir(checkJSONDir)

        #check if JSONFiles folder exists
        #if not, create it

        JSONFileFolder = os.listdir(checkJSONDir)
        JSONFile = []
        captionData = []

        for file in JSONFileFolder:
            if file.endswith(".json"):
                filepath = os.path.join(checkJSONDir, file)
                with open(filepath, 'r', encoding="utf8") as tempJSONFile:
                    jsonData = json.loads(tempJSONFile.read())
                    for i in range(len(jsonData)):
                        captionData.append(jsonData[i]['caption'])
        return captionData

    except:
        print("exception")
        return None

def create_dict():
    lst = tp.doShadyStuff()
    dictonary = dict(lst)
    return dictonary

