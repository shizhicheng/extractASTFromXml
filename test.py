from vectorizer.model.constVariable import leaveDicPath, methodNameDicPath, midNodeEmbeddingPath
import pickle
if __name__=="__main__":
    with open(midNodeEmbeddingPath,"rb") as f:
        midNodeEmbedding=pickle.load(f)
        print(midNodeEmbedding[0])
        print(midNodeEmbedding[1])




