# Source code of the algorithms and experiments of the paper "Fourier Transform-based Surrogates for Permutation Problems" (published in GECCO 2023)

This repository contains the source code of the paper:

* Francisco Chicano, Bilel Derbel and Sébastien Verel, "Fourier Transform-based Surrogates for Permutation Problems", In Genetic and Evolutionary Computation Conference (GECCO), 2023. DOI: 10.1145/3583131.3590425

The instances of the Asteroid Routing Problem (ARP) and the Single Machine Total Weighted Tardines Problem (SMTWTP) can be found in Zenodo at URL: https://doi.org/10.5281/zenodo.7850763
. The Zenodo package also contains the results of the experiments shown in the GECCO 2023 paper.

The three shell scripts show how to run the code. These scripts do the following:

* 1-launch-experiments-fft.sh: It computes the Fourier transform of the given instance of the problem
* 1-launch-experiments-learning.sh: It computes the surrogate model using linear regression
* 1-launch-experiments.sh: It computes the truncated model basedon the real Fourier transform



