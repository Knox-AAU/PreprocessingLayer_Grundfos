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
    tuples = []




    for c in list_of_captions:
        if c in dictionary:
            c = c.replace("CU 300", "CU-300")
        split = c.split(" ")
        if "Fig" in c:
            split[0]= split[0]+" " + split[1] + " "
            split.pop(1)
        for s in split:
            if s == "CU-300":
                s = s.replace("-"," ")
            if dictonary.get(s) is not None:
                tuples.append((s, dictonary.get(s)))
            else:
                tuples.append((s, "O"))
    return tuples





if __name__ == "__main__":
    test = extract_JSON.importJSON()
    dictonary = extract_JSON.create_dict()
    dictonary.pop("Name")
    tuples = check_for_keywords(test, dictonary)
    print(tuples)

    NER.vectorization(tuples)
    NER.leTrain()



