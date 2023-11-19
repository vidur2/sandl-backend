from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import numpy as np
import random

class Model:
    def __init__(self, prompt: str, model = None):
        self.prompt = prompt
        if (model == None):
            self.model = SentenceTransformer("all-MiniLM-L6-v2", device="mps")
        else:
            self.model = model
    def __call__(self):
        out = self.model.encode(self.prompt, normalize_embeddings=True)
        y = [out]
        sum = 0
        vlowF = './model/iso_forest_vlow'
        lowF = './model/iso_forest_low'
        medF = './model/iso_forest_med'
        highF = './model/iso_forest_high'
        vhighF = './model/iso_forest_vhigh'
        for i in range(5):
            iso_forest_vlow = pickle.load(open((vlowF + str(i) + '.sav'), 'rb'))
            iso_forest_low = pickle.load(open((lowF + str(i) + '.sav'), 'rb'))
            iso_forest_med = pickle.load(open((medF + str(i) + '.sav'), 'rb'))
            iso_forest_high = pickle.load(open((highF + str(i) + '.sav'), 'rb'))
            iso_forest_vhigh = pickle.load(open((vhighF + str(i) + '.sav'), 'rb'))
            sum += iso_forest_vlow.predict(y) + iso_forest_low.predict(y) + iso_forest_med.predict(y) + iso_forest_high.predict(y) + iso_forest_vhigh.predict(y)
        return ((sum/25)+1)/2
    def hash(self):
        vectorizer = TfidfVectorizer()
        return str([np.base_repr(int(i * 10), base=8) for i in vectorizer.fit_transform([self.prompt]).toarray().tolist()[0]])


if (__name__ == "__main__"):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    n = 1000
    for i in range(n):
        print(model.encode("The National Basketball Association's Rookie of the Year Award is an annual National Basketball Association (NBA) award given to the top rookie(s) of the regular season. Initiated following the 1952–53 NBA season, it confers the"))