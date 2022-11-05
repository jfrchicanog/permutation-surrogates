import torch
from Snob2 import SnElement, SnFunction

class FunctionFromSamples:
	fn = None
	n = None
	globalMin = None
	globalMax = None

	def __init__(self, file):
		f = open(file,'r')
		for l in f.readlines():
			a = l.split(',')
			perm = [i+1 for i in map(int,a[1].split())]
			if self.fn == None:
				self.n = len(perm)
				self.fn = SnFunction.zero(self.n)

			val = float(a[0])
			self.fn[SnElement(perm)] = val
			if self.globalMin == None or val < self.globalMin:
				self.globalMin=val
			if self.globalMax == None or val > self.globalMax:
				self.globalMax=val


		f.close()

	def evaluate(self, permutation):
		return self.fn[SnElement(permutation)]

	def getN(self):
		return self.n

	def getFunction(self):
		return self.fn
