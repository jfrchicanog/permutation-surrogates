from Snob2 import Sn, ClausenFFT, SnElement, SnType, IntegerPartitions, SnIrrep, SnVec, SnPart
import numpy as np
from sklearn import linear_model
import itertools

class SurrogateModel:
	originalFunction = None
	listOfIrreps = None
	fourierTransformCoefficients = None
	fft = None
	n = None
	nfactorial = None
	trainingSamples = None
	def __init__(self, function, fType):
		self.originalFunction = function
		if (len(fType) == 0):
			raise ValueError("The list of irreps is empty")
		self.n = fType[0].getn()
		self.nfactorial = len(Sn(self.n))
		for irrep in fType:
			if irrep.getn() != self.n:
				raise ValueError("All irreps should have the same dimension")
		self.listOfIrreps = list(fType)
		self.listOfIrreps.sort()
		self.fft = ClausenFFT(self.n)

	def resetTrainingSamples(self):
		self.trainingSamples = [permutation for permutation in itertools.permutations(range(1, self.n + 1))]

	def getCoordinates(self, permutation):
		coordinates = list()
		pi = SnElement(permutation)
		for irrep in self.listOfIrreps:
			d = irrep.get_dim()
			m = irrep[pi] * d * (1.0/ self.nfactorial)
			coordinates += [m[i,j] for i in range(0,d) for j in range(0,d)]
		return coordinates

	def train(self, samples, randomSeed=0):
		#self.fourierTransformCoefficients = linear_model.Ridge(alpha=0.000001,fit_intercept=False)
		self.fourierTransformCoefficients = linear_model.Lasso(alpha=0.000001,fit_intercept=False)
		#self.fourierTransformCoefficients = linear_model.LassoCV(fit_intercept=False)
		#self.fourierTransformCoefficients = linear_model.LassoLarsCV(fit_intercept=False)
		#self.fourierTransformCoefficients = linear_model.RidgeCV(fit_intercept=False,alphas=np.logspace(-8,-3,13))
		#self.fourierTransformCoefficients = linear_model.Lars(n_nonzero_coefs=np.inf, normalize=False, fit_intercept=False)
		#self.fourierTransformCoefficients = linear_model.LinearRegression(fit_intercept=False)
		coordinateList = list()
		valuesList = list()
		self.resetTrainingSamples()
		np.random.seed(randomSeed)
		for sample in range(0,samples):
			index = np.random.randint(sample,len(self.trainingSamples))
			permutation = self.trainingSamples[index]
			self.trainingSamples[sample], self.trainingSamples[index] = self.trainingSamples[index], self.trainingSamples[sample]
			coordinateList.append(self.getCoordinates(permutation))
			valuesList.append(self.originalFunction.evaluate(permutation))
		self.fourierTransformCoefficients.fit(coordinateList, valuesList)

	def getFunction(self):
		sntype = SnType()
		lambd = IntegerPartitions(self.n)
		for i in range(len(lambd)):
			irrep = SnIrrep(lambd[i])
			sntype[irrep.get_lambda()] = irrep.get_dim()

		fourierTransform = SnVec.zero(sntype)

		index = 0
		for irrep in self.listOfIrreps:
			d = irrep.get_dim()
			part = SnPart.zero(irrep.get_lambda(),d)
			for i in range(0,d):
				for j in range(0,d):
					# In the linst below the indices should be part[i,j], but it seems to be an error in ClausenFFT that makes the matrices to be transposed
					part[j,i] = self.fourierTransformCoefficients.coef_[index]
					index += 1
			fourierTransform[irrep.get_lambda()] = part
		#print(fourierTransform)
		return self.fft.inv(fourierTransform)

