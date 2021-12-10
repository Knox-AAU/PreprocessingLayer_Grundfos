import os
import json
import pathlib
import csv
import sys


"""
    1. IMPORT CSV OG LAV DICT
    2. INDLÆS JSON CAPTIONS
    3. GIV ALLE ORD I CAPTIONS ET TAG, OG LAV ET ARRAY AF ARRAYS MED VORES TUPLE
    4. GEM DISSE TUPLE SOM .CSV, SÅ VORES DATASÆT LIGNER DET FRA KAGGLE
"""

#1 IMPORT CSV OG LAV DICT
def import_csv():
    with open(os.path.join(pathlib.Path(__file__).parent.parent, 'data_acquisition/products.csv')) as f:
        data = [tuple(line) for line in csv.reader(f)]
    return data

#1.5 lav data om til dict
def create_dict(data):
    return dict(data)


# 2. IMPORT JSON CAPTIONS
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




#3. GIV ALLE ORD I CAPTIONS ET TAG, OG LAV ET ARRAY AF ARRAYS MED VORES TUPLE
def create_tuples(list_of_captions: str, dictionary: dict):
    captions = []
    for c in list_of_captions:
        tuples = []
        split = c.split(" ")
        if ("Fig" or "Figure") in c:
            split[0] = split[0] + " " + split[1] + " "
            split.pop(1)
        for x in range(len(split)-1):
            if dictionary.get(split[x] + " " + split[x+1]) is not None:
                split[x] = split[x] + " " + split[x+1]
                split[x+1] = ""
                x = x + 1
            elif split[x] == "DMH":
                split[x] = split[x] + " " + split[x + 1]
                split[x + 1] = ""
                x = x + 1
        for s in split:
            if s != "" and not s.isdecimal():
                if dictionary.get(s) is not None:
                    tuples.append((s, dictionary.get(s)))
                elif "DMH" in s:
                    tuples.append((s, "dc drives"))
                else:
                    tuples.append((s, "O"))
        captions.append(tuples)
    return captions

def create_csv_dataset(tuples):
    with open("csv_dataset.csv", "w", encoding="utf8") as f:
        write = csv.writer(f, sys.stdout, lineterminator='\n')
        header = ['Sentence #', "Word", 'Tag']
        write.writerow(header)
        sentence = 1
        for t in tuples:
            for x in range(len(t)):
                if x == 0:
                    body = [f"Sentence {sentence}", t[x][0], t[x][1]]
                else:
                    body = [None, t[x][0], t[x][1]]
                write.writerow(body)
            sentence += 1


if __name__ == "__main__":
    print("NER 2")
    csv_data = import_csv()
    dictionary = create_dict(csv_data)
    captions = importJSON()
    tuples = create_tuples(captions, dictionary)
    #print(tuples)
    create_csv_dataset(tuples)