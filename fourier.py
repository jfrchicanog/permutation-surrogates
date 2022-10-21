import torch
import cnine
import Snob2
import sys
import itertools
from ast import literal_eval

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


if __name__ == '__main__':
	instance = SMWTP(sys.argv[1])
	output = sys.argv[2]
	f = open(output, "w")
	n = instance.getN()
	fft = Snob2.ClausenFFT(n)
	F = instance.getFourierTransform()
	m = F.get_type().get_map()
	f1 = instance.getFunction()

	#print(f'Global min: {instance.globalMin}')
	#print(f'Global max: {instance.globalMax}')
		
	f.write('Max order\tMAE\tNormalized MAE\tF1 Min\tF1 Max\tF2 Min\tF2 Max\n')
	for firstLine in range(0,n):
		for irrep in m:
			if irrep[0] == firstLine:
				F[irrep] = Snob2.SnPart.zero(irrep, m[irrep])
		f2 = fft.inv(F)
		val, f1Min, f1Max, f2Min, f2Max = maeMaxMin(f1, f2, F.get_n())
		f.write(f'{n-firstLine-1}\t{val}\t{val/(instance.globalMax-instance.globalMin)}\t{f1Min}\t{f1Max}\t{f2Min}\t{f2Max}\n')
	
	f.close()
	