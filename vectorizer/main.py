from vectorizer.sampling import getSamples, batchSamples
from vectorizer.parameters import  samplePath
from vectorizer.network.train import learn_vectors
from vectorizer.parameters import logdir, outfile
from vectorizer.parameters import trainPath

# 获得训练样本
samples = getSamples(samplePath, sampleType="train")

learn_vectors(samples,logdir,outfile)


