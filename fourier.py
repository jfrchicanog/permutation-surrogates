import torch
import cnine
from sklearn import linear_model
import Snob2
import sys
import itertools
import numpy as np
from ast import literal_eval

from smwtp import SMWTP

global TOLERANCE

TOLERANCE = 0.001


class SurrogateModel:
	originalFunction = None
	listOfIrreps = None
	fourierTransformCoefficients = None
	fft = None
	n = None
	nfactorial = None
	def __init__(self, function, fType):
		self.originalFunction = function
		if (len(fType) == 0):
			raise ValueError("The list of irreps is empty")
		self.n = fType[0].getn()
		self.nfactorial = len(Snob2.Sn(self.n))
		for irrep in fType:
			if irrep.getn() != self.n:
				raise ValueError("All irreps should have the same dimension")
		self.listOfIrreps = list(fType)
		self.listOfIrreps.sort()
		self.fft = Snob2.ClausenFFT(self.n)


	def getCoordinates(self, permutation):
		coordinates = list()
		pi = Snob2.SnElement(permutation)
		for irrep in self.listOfIrreps:
			d = irrep.get_dim()
			m = irrep[pi] * d * (1.0/ self.nfactorial)
			coordinates += [m[i,j] for i in range(0,d) for j in range(0,d)]
		return coordinates

	def train(self, samples, randomSeed=0):
		self.fourierTransformCoefficients = linear_model.Lars(n_nonzero_coefs=np.inf, normalize=False, fit_intercept=False)
		#self.fourierTransformCoefficients = linear_model.LinearRegression(normalize=False, fit_intercept=False)
		coordinateList = list()
		valuesList = list()
		np.random.seed(randomSeed)
		for sample in range(0,samples):
			permutation = np.random.permutation(range(1,self.n+1))
			coordinateList.append(self.getCoordinates(permutation))
			valuesList.append(self.originalFunction.evaluate(permutation))
		self.fourierTransformCoefficients.fit(coordinateList, valuesList)

	def getFunction(self):
		sntype = Snob2.SnType()
		lambd = Snob2.IntegerPartitions(self.n)
		for i in range(len(lambd)):
			irrep = Snob2.SnIrrep(lambd[i])
			sntype[irrep.get_lambda()] = irrep.get_dim()

		fourierTransform = Snob2.SnVec.zero(sntype)

		index = 0
		for irrep in self.listOfIrreps:
			d = irrep.get_dim()
			part = Snob2.SnPart.zero(irrep.get_lambda(),d)
			for i in range(0,d):
				for j in range(0,d):
					part[j,i] = self.fourierTransformCoefficients.coef_[index]
					index += 1
			fourierTransform[irrep.get_lambda()] = part
		print(fourierTransform)
		return self.fft.inv(fourierTransform)



def maeMaxMin(f1, f2, n):
	sum, f1Min, f1Max, f2Min, f2Max = (0,None,None,None,None)
	for permutation in itertools.permutations(range(1,n+1)):
		valF1 = f1[Snob2.SnElement(permutation)]
		valF2 = f2[Snob2.SnElement(permutation)]
		if f1Min == None or valF1 < f1Min:
			f1Min = valF1
		if f1Max == None or valF1 > f1Max:
			f1Max = valF1
		if f2Min == None or valF2 < f2Min:
			f2Min = valF2
		if f2Max == None or valF2 > f2Max:
			f2Max = valF2
		sum = sum + abs(valF1-valF2)
	return (sum/len(f1), f1Min, f1Max, f2Min, f2Max)

def maeOfGlobalOptima(f1, f2, n):
	sumF1 = 0
	globalOptimaValueF1 = None
	globalOptimaF1 = 0
	sumF2 = 0
	globalOptimaValueF2 = None
	globalOptimaF2 = 0

	globalOptimaF2List = list()

	for permutation in itertools.permutations(range(1,n+1)):
		valF1 = f1[Snob2.SnElement(permutation)]
		valF2 = f2[Snob2.SnElement(permutation)]
		if globalOptimaValueF1 == None or valF1 < globalOptimaValueF1:
			globalOptimaValueF1 = valF1
			sumF1 = abs(valF1-valF2)
			globalOptimaF1 = 1
		elif valF1 == globalOptimaValueF1:
			sumF1 = sumF1 + abs(valF1-valF2)
			globalOptimaF1 = globalOptimaF1 + 1

		if globalOptimaValueF2 == None or valF2 < globalOptimaValueF2:
			globalOptimaValueF2 = valF2
			sumF2 = abs(valF1-valF2)
			globalOptimaF2 = 1
			globalOptimaF2List = [permutation]
		elif valF2 == globalOptimaValueF2:
			sumF2 = sumF2 + abs(valF1-valF2)
			globalOptimaF2 = globalOptimaF2 + 1
			globalOptimaF2List.append(permutation)

	preservedGlobalOptima = len([permutation for permutation in globalOptimaF2List if f1[Snob2.SnElement(permutation)]==globalOptimaValueF1])


	return sumF1/globalOptimaF1, globalOptimaF1, sumF2/globalOptimaF2, globalOptimaF2, preservedGlobalOptima

def allPermutations(n):
	return [Snob2.SnElement(permutation) for permutation in itertools.permutations(range(1, n + 1))]

def sortedPermutations(n, f):
	list = allPermutations(n)
	list.sort(key=(lambda p: f[p]))
	return list

def permutationRanking(n, f):
	permutations = sortedPermutations(n,f)
	result = Snob2.SnFunction.zero(n)

	previousValue = None
	rank = 0
	for p in permutations:
		if previousValue == None or f[p] > previousValue + TOLERANCE:
			rank = rank+1
			previousValue = f[p]
		result[p] = rank

	return result


def showNormalOrder(n, f):
	print("Normal order")
	for p in allPermutations(n):
		print(f'{p}\t{f[p]}')


def showSortedOrder(n, f):
	print("Sorted permutations")
	for p in sortedPermutations(n, f):
		print(f'{p}\t{f[p]}')


def showPermutationRanking(n, f):
	print("Permutation ranking")
	ranking = permutationRanking(n, f)
	for p in allPermutations(n):
		print(f'{p}\t{ranking[p]}')

def experiment():
	instance = SMWTP('SMTWTP_small/n4.txt')
	sm = SurrogateModel(instance, [Snob2.SnIrrep([4]), Snob2.SnIrrep([3, 1]),
										   Snob2.SnIrrep([2, 2]), Snob2.SnIrrep([2, 1, 1]),
										   Snob2.SnIrrep([1, 1, 1, 1])])
	sm.train(10)
	fn=sm.getFunction()
	print(instance.getFourierTransform())
	print(fn)
	print(instance.getFunction())

def analysis(instance, output):
	f = open(output, "w")
	n = instance.getN()
	f1 = instance.getFunction()

	fft = Snob2.ClausenFFT(n)
	F = fft(f1)
	m = F.get_type().get_map()

	#showNormalOrder(n, f1)
	#showSortedOrder(n, f1)
	#showPermutationRanking(n, f1)
	#print(f'Global min: {instance.globalMin}')
	#print(f'Global max: {instance.globalMax}')
	#print("f1")
	#showSortedOrder(n, f1)
	rankingF1 = permutationRanking(n, f1)
	#print("Ranking f1")
	#showNormalOrder(n, rankingF1)
	f.write('Max order\tMAE\tNormalized MAE\tF1 Min\tF1 Max\tF2 Min\tF2 Max\tMAE-GO Orig\tNormalized MAE-GO Orig\tGO Orig\tMAE-GO Trunc\tNormalized MAE-GO Trunc\tGO Trunc\tRanking MAE\tPreserved GO\n')
	for firstLine in range(0,n):
		for irrep in m:
			if irrep[0] == firstLine:
				F[irrep] = Snob2.SnPart.zero(irrep, m[irrep])
		f2 = fft.inv(F)
		#showPermutationRanking(n, f2)
		val, f1Min, f1Max, f2Min, f2Max = maeMaxMin(f1, f2, F.get_n())
		fRange = (instance.globalMax-instance.globalMin)
		maeGOF1, globalOptimaF1, maeGOF2, globalOptimaF2, preservedGlobalOptima = maeOfGlobalOptima(f1, f2, F.get_n())

		rankingF2 = permutationRanking(n, f2)
		#print("f2")
		#showSortedOrder(n, f2)
		#print("Ranking f2")
		#showSortedOrder(n,rankingF2)
		maeRanking, _, _, _, _ = maeMaxMin(rankingF1, rankingF2, n)
		f.write(f'{n-firstLine-1}\t{val}\t{val/fRange}\t{f1Min}\t{f1Max}\t{f2Min}\t{f2Max}\t{maeGOF1}\t{maeGOF1 / fRange}\t{globalOptimaF1}\t{maeGOF2}\t{maeGOF2 / fRange}\t{globalOptimaF2}\t{maeRanking}\t{preservedGlobalOptima}\n')
	
	f.close()



if __name__ == '__main__':
	from argparse import ArgumentParser,RawDescriptionHelpFormatter,_StoreTrueAction,ArgumentDefaultsHelpFormatter,Action
	parser = ArgumentParser(description = "Permutation surrogates")
	parser.add_argument('--problem', type=str, help='Problem: smwtp, samples')
	parser.add_argument('--instance', type=str, help='instance file')
	parser.add_argument("--output", type=str, default=None, help="output file")
	args = parser.parse_args()

	if args.problem == 'smwtp':
		from smwtp import SMWTP
		instance = SMWTP(args.instance)
	elif args.problem == 'samples':
		from functionsamples import FunctionFromSamples
		instance = FunctionFromSamples(args.instance)
	else:
		raise ValueError(f'Unsupported problem: {args.problem}')

	analysis(instance, args.output)
