import pandas as pd
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text


class labelGenerator:
	def __init__(self, figureDataPath = "../OUTPUT_PRUNED"):
		self.figureDataPath = figureDataPath
		self.captionList = []
		self.idList = []
		self.load_json(self.figureDataPath)
		self.df = self.generate_scores(self.captionList, self.idList)
		self.colList = self.df.columns.values.tolist()
		print(self.colList)
		print()

	def get_filename(self, file):
		filename, file_extension = os.path.splitext(file)
		return filename

	def load_json(self, figureDataPath):
		for file in os.listdir(figureDataPath):
			pdfID = self.get_filename(file)
			print(pdfID)	
			
			with open(os.path.join(figureDataPath, file), encoding="utf8") as figureData:
				pdfJSON = json.load(figureData, encoding="utf8")
				
				for fig in pdfJSON:
					self.captionList.append(fig["caption"])
					self.idList.append(fig["figID"])

	def generate_scores(self, captionList, idList):
		myStopWords = text.ENGLISH_STOP_WORDS
		vectorizer = TfidfVectorizer(stop_words = myStopWords)
		vectors = vectorizer.fit_transform(captionList)
		feature_names = vectorizer.get_feature_names_out()
		dense = vectors.todense()
		denselist = dense.tolist()
		df = pd.DataFrame(denselist, columns=feature_names, index = idList)

		return df




	def get_label(self, id, max_labels):
		self.colList.sort(key=lambda col: self.df.loc[id, col])
		self.colList.reverse()
		result = list(filter(lambda col: (self.df.loc[id, col] != 0), self.colList))

		print(id)
		print(result[0:max_labels])
		return result[0:max_labels]

labelGen = labelGenerator()

for id in labelGen.idList:
    labelGen.get_label(id, 5)