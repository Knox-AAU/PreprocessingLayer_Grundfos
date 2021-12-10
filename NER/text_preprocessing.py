import os
import pathlib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

import NER
import extract_JSON

def doShadyStuff():

    plt.style.use("ggplot")
    data = pd.read_csv(os.path.join(pathlib.Path(__file__).parent.parent, 'data_acquisition/products.csv'), encoding="latin1")
    data = data.fillna(method="ffill")
    data.tail(12)
    words = set(list(data['Name'].values))
    words.add('PADword')
    n_words = len(words)
    tags = list(set(data["Tag"].values))
    n_tags = len(tags)

    print(n_words)
    print(data)
    print(n_tags)

    with open(os.path.join(pathlib.Path(__file__).parent.parent, 'data_acquisition/products.csv')) as f:
        data = [tuple(line) for line in csv.reader(f)]


    largest_sen = max(len(sen) for sen in data)
    print('biggest sentence has {} words'.format(largest_sen))
    return data

def check_for_keywords(list_of_captions: str, dictionary: dict):
    captions = []
    for c in list_of_captions:
        tuples = []
        split = c.split(" ")
        if ("Fig" or "Figure") in c:
            split[0] = split[0] + " " + split[1] + " "
            split.pop(1)
        for x in range(len(split)-1):
            if dictonary.get(split[x] + " " + split[x+1]) is not None:
                split[x] = split[x] + " " + split[x+1]
                split[x+1] = ""
                x = x + 1
        for s in split:
            if s != "":
                if dictonary.get(s) is not None:
                    tuples.append((s, dictonary.get(s)))
                else:
                    tuples.append((s, "O"))
        captions.append(tuples)
    return captions





if __name__ == "__main__":
    #test = extract_JSON.importJSON()
    dictonary = extract_JSON.create_dict()
    dictonary.pop("Name")
    tuples = check_for_keywords(test, dictonary)
    print(tuples)

    #NER.vectorization(tuples)
    #NER.leTrain()



