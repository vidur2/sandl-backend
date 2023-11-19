from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
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
        # Put through SVM to get value
        return random.random()
    def hash(self):
        vectorizer = TfidfVectorizer()
        return str([np.base_repr(int(i * 10), base=8) for i in vectorizer.fit_transform([self.prompt]).toarray().tolist()[0]])


if (__name__ == "__main__"):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    n = 1000
    for i in range(n):
        print(model.encode("The National Basketball Association's Rookie of the Year Award is an annual National Basketball Association (NBA) award given to the top rookie(s) of the regular season. Initiated following the 1952–53 NBA season, it confers the"))