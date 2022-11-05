import torch
from Snob2 import SnElement, SnFunction, ClausenFFT
import itertools

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
		f = SnFunction.zero(n)
		for permutation in itertools.permutations(range(1,n+1)):
			val = self.evaluate(permutation)
			f[SnElement(permutation)]=val
			if self.globalMin == None or val < self.globalMin:
				self.globalMin=val
			if self.globalMax == None or val > self.globalMax:
				self.globalMax=val

		return f
