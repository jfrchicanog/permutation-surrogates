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

def mae(f1, f2, n):
	sum = 0
	for permutation in itertools.permutations(range(1,n+1)):
		sum = sum + abs(f1[Snob2.SnElement(permutation)]-f2[Snob2.SnElement(permutation)])
	return sum/len(f1)


if __name__ == '__main__':
	instance = SMWTP(sys.argv[1])
	irreps = [Snob2.IntegerPartition(literal_eval(sys.argv[i])) for i in range(2,len(sys.argv))]
	#print(irreps)
	F = instance.getFourierTransform()
	#print(F)
	m = F.get_type().get_map()
	for irrep in m:
		if irrep not in irreps:
			F[irrep] = Snob2.SnPart.zero(irrep, m[irrep])

	fft = Snob2.ClausenFFT(F.get_n())
	f2 = fft.inv(F)
	f1 = instance.getFunction()
	val = mae(f1, f2, F.get_n())
	#print(F)
	print(f'Global min: {instance.globalMin}')
	print(f'Global max: {instance.globalMax}')
	print(f'MAE: {val}')
	print(f'Normalized MAE: {val/(instance.globalMax-instance.globalMin)}')
	



