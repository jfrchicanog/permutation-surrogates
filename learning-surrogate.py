import torch
import cnine
import Snob2
import sys
import itertools
from surrogate import SurrogateModel
from ast import literal_eval

from smwtp import SMWTP

global TOLERANCE
TOLERANCE = 0.001

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

def learningAnalysis(instance, trainingStart, trainingEnd, trainingIncrement, randomSeed, irreps, output):
    sm = SurrogateModel(instance, irreps)
    f = open(output, "w")
    n = instance.getN()
    f1 = instance.getFunction()
    f.write('Samples\tMAE\tNormalized MAE\tF1 Min\tF1 Max\tF2 Min\tF2 Max\tMAE-GO Orig\tNormalized MAE-GO Orig\tGO Orig\tMAE-GO Trunc\tNormalized MAE-GO Trunc\tGO Trunc\tRanking MAE\tPreserved GO\n')

    for training in range(trainingStart, trainingEnd+1, trainingIncrement):
        sm.train(training, randomSeed=randomSeed)
        f2=sm.getFunction()
        val, f1Min, f1Max, f2Min, f2Max = maeMaxMin(f1, f2, n)
        fRange = (instance.globalMax-instance.globalMin)
        maeGOF1, globalOptimaF1, maeGOF2, globalOptimaF2, preservedGlobalOptima = maeOfGlobalOptima(f1, f2, n)

        rankingF2 = permutationRanking(n, f2)
        rankingF1 = permutationRanking(n, f1)
        maeRanking, _, _, _, _ = maeMaxMin(rankingF1, rankingF2, n)
        f.write(f'{training}\t{val}\t{val/fRange}\t{f1Min}\t{f1Max}\t{f2Min}\t{f2Max}\t{maeGOF1}\t{maeGOF1 / fRange}\t{globalOptimaF1}\t{maeGOF2}\t{maeGOF2 / fRange}\t{globalOptimaF2}\t{maeRanking}\t{preservedGlobalOptima}\n')
        f.flush()

    f.close()

if __name__ == '__main__':
    from argparse import ArgumentParser,RawDescriptionHelpFormatter,_StoreTrueAction,ArgumentDefaultsHelpFormatter,Action
    parser = ArgumentParser(description = "Permutation surrogates")
    parser.add_argument('--problem', type=str, help='Problem: smwtp, samples')
    parser.add_argument('--instance', type=str, help='instance file')
    parser.add_argument('--trainingStart', type=int, help='initial value for the number of training samples')
    parser.add_argument('--trainingEnd', type=int, help='final value for the number of training samples')
    parser.add_argument('--trainingIncrement', type=int, help='increment value for the number of training samples')
    parser.add_argument('--randomSeed', type=int, help='random seed used in the sorting of training samples')
    parser.add_argument('--irreps', type=str, help='irreps to learn')
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

    irreps = [Snob2.SnIrrep(e) for e in literal_eval(args.irreps)]
    learningAnalysis(instance, args.trainingStart, args.trainingEnd, args.trainingIncrement, args.randomSeed, irreps, args.output)


