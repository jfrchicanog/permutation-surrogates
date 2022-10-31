import torch
import cnine
import Snob2
import sys
import itertools
from ast import literal_eval

global TOLERANCE

TOLERANCE = 0.001

class SMWTP:
	times = []
	weights = []
	due = []
	globalMin = None
	globalMax = None
	def __init__(self, file):
		with open(file) as f:
			lines = f.readlines()
			n = int(lines[0])
			for line in lines[1:]:
				elements = line.split()
				self.times.append(float(elements[0]))
				self.weights.append(float(elements[1]))
				self.due.append(float(elements[2]))
			if n != len(self.times):
				print("Warning: elements count does not match")

	def evaluate(self, permutation):
		t = 0
		fit = 0
		for i in range(len(self.times)):
			job = permutation[i]-1
			t = t + self.times[job]
			if t > self.due[job]:
				fit = fit + self.weights[job] * (t - self.due[job])

		return fit

	def getN(self):
		return len(self.times)


	def getFunction(self):
		n = len(self.times)
		f = Snob2.SnFunction.zero(n)
		for permutation in itertools.permutations(range(1,n+1)):
			val = self.evaluate(permutation)
			f[Snob2.SnElement(permutation)]=val
			if self.globalMin == None or val < self.globalMin:
				self.globalMin=val
			if self.globalMax == None or val > self.globalMax:
				self.globalMax=val

		return f

	def getFourierTransform(self):
		fft = Snob2.ClausenFFT(self.getN())
		return fft(self.getFunction())


class SurrogateModel:
	originalFunction = None
	listOfIrreps = list()
	fourierTransform = None
	n = None
	fft = None
	def __init__(self, n, function, fType):
		self.originalFunction = function
		self.listOfIrreps = fType
		self.listOfIrreps.sort()
		self.fft = Snob2.ClausenFFT(n)


	def getCoordinates(self, permutation):
		coordinates = list()

		for irrep in self.listOfIrreps:
			d = irrep.get_dim()
			pi = Snob2.SnElement(permutation)
			m = irrep[pi] * d
			coordinates += [m[i,j] for i in range(0,d) for j in range(0,d)]

		#rho=SnIrrep([3,1])
		#rho.get_dim()
		#pi=SnElement([3,2,1,4])
		#a=rho[pi]
		#a.ndims()
		#a.dim(0)
		#a.dim(1)
		#a[i,j]

		return coordinates

	def train(self, samples, randomSeed=0):
		pass

		# Build the omdel with the number of samples required

	def getFunction(self):
		return fft.inv(fourierTransform)



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


if __name__ == '__main__':
	instance = SMWTP(sys.argv[1])
	output = sys.argv[2]
	f = open(output, "w")
	n = instance.getN()
	fft = Snob2.ClausenFFT(n)
	F = instance.getFourierTransform()
	m = F.get_type().get_map()
	f1 = instance.getFunction()

	#showNormalOrder(n, f1)
	#showSortedOrder(n, f1)
	#showPermutationRanking(n, f1)
	#print(f'Global min: {instance.globalMin}')
	#print(f'Global max: {instance.globalMax}')
	print("f1")
	showSortedOrder(n, f1)
	rankingF1 = permutationRanking(n, f1)
	print("Ranking f1")
	showNormalOrder(n, rankingF1)
	f.write('Max order\tMAE\tNormalized MAE\tF1 Min\tF1 Max\tF2 Min\tF2 Max\tMAE-GO Orig\tNormalized MAE-GO Orig\tGO Orig\tMAE-GO Trunc\tNormalized MAE-GO Trunc\tGO Trunc\tRanking MAE\tPreserved GO\n')
	for firstLine in range(0,n):
		for irrep in m:
			if irrep[0] == firstLine:
				F[irrep] = Snob2.SnPart.zero(irrep, m[irrep])
		f2 = fft.inv(F)
		showPermutationRanking(n, f2)
		val, f1Min, f1Max, f2Min, f2Max = maeMaxMin(f1, f2, F.get_n())
		fRange = (instance.globalMax-instance.globalMin)
		maeGOF1, globalOptimaF1, maeGOF2, globalOptimaF2, preservedGlobalOptima = maeOfGlobalOptima(f1, f2, F.get_n())

		rankingF2 = permutationRanking(n, f2)
		print("f2")
		showSortedOrder(n, f2)
		print("Ranking f2")
		showSortedOrder(n,rankingF2)
		maeRanking, _, _, _, _ = maeMaxMin(rankingF1, rankingF2, n)
		f.write(f'{n-firstLine-1}\t{val}\t{val/fRange}\t{f1Min}\t{f1Max}\t{f2Min}\t{f2Max}\t{maeGOF1}\t{maeGOF1 / fRange}\t{globalOptimaF1}\t{maeGOF2}\t{maeGOF2 / fRange}\t{globalOptimaF2}\t{maeRanking}\t{preservedGlobalOptima}\n')
	
	f.close()
	