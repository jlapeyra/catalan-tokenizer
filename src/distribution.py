from collections import Counter, defaultdict
from io import TextIOWrapper
import math
from typing import Sequence
import numpy as np
from utils import id, windowed, key_list
from itertools import chain
from abc import ABC, abstractmethod


ALPHA = 0.1

class Distribution(Counter):
    # Counter allows __add__

    def add(self, item):
        self[item] += 1
    
    def probability(self, key, alpha:float=ALPHA, num_keys:int=None):
        return (self[key] + alpha)/(self.total() + alpha*(num_keys or len(self.keys())))
    
    def logProbability(self, key, alpha:float=ALPHA, num_keys:int=None):
        return math.log(self.probability(key, alpha, num_keys), 2)

    def probabilityDistribution(self, alpha:float=ALPHA, num_keys:int=None):
        return Distribution({key: self.probability(key, alpha, num_keys) for key in self.keys()})
    
    def logProbabilityDistribution(self, alpha:float=ALPHA, num_keys:int=None):
        return Distribution({key: self.logProbability(key, alpha, num_keys) for key in self.keys()})


class DoubleKeyDict:
    @abstractmethod
    def get(self, k1, k2):
        pass

    @abstractmethod
    def priorKeys(self) -> set:
        pass

    @abstractmethod
    def posteriorKeys(self) -> set:
        pass

    def matrix(self) -> np.ndarray:
        priors = sorted(self.priorKeys())
        posteriors = sorted(self.posteriorKeys())
        matrix = np.zeros((len(priors), len(posteriors)))
        for i, p in enumerate(priors):
            for j, q in enumerate(posteriors):
                matrix[i, j] = self.get(p, q)
        return matrix, priors, posteriors


class ConditionalDistribution(defaultdict[object, Distribution], DoubleKeyDict):
    # counter allows __add__

    def __init__(self) -> None:
        super().__init__(Distribution)

    def add(self, key1, key2, num=1):
        self[key1][key2] += num

    def __add__(self, other:'ConditionalDistribution'):
        if isinstance(other, ConditionalDistribution):
            for key in other.keys():
                self[key] += other[key]

    def save(self, file:TextIOWrapper):
        for keys, count in sorted(self.items()):
            print(*keys, count, file=file)
                
    def load(self, file:TextIOWrapper):
        for line in file.readlines():
            try:
                key1, key2, count = line.strip('\n').split()
                count = int(count)
            except:
                raise Exception(f'Wrong format: expected `key1 key2 num`. Got: "{line}"')
            else:
                self[key1][key2] = count
        return self
    
    def priorKeys(self):
        return set(self.keys())
    
    def posteriorKeys(self):
        return set().union(*(dist.keys() for dist in self.values()))
    
pass

    
class NGram(Counter, DoubleKeyDict):
    # Counter allows __add__

    def __init__(self, n:int, default=None, prune_prior=id, prune_posterior=id, prune=None) -> None:
        self.n = n
        self.default = default
        if prune is not None:
            self.prune_posterior = prune
            self.prune_prior = prune
        else:
            self.prune_prior = prune_prior
            self.prune_posterior = prune_posterior
        super().__init__()

    def __sliding_window(self, sequence:Sequence):
        head, tail = [self.default]*(self.n-1), [self.default]
        prior     = map(self.prune_prior, sequence)
        posterior = map(self.prune_posterior, sequence)
        prior     = chain(head, prior)
        posterior = chain(posterior, tail)
        return zip(windowed(prior, self.n-1), posterior)

    def feed(self, sequence:Sequence):
        super().update(self.__sliding_window(sequence))
        return self
    
    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for (prior, posterior), count in sorted(self.items()):
                print(*prior, posterior, count, file=f)
                
    def load(self, filename, reverse=False):
        with open(filename, 'w', encoding='utf-8') as f:
            for line in f:
                try:
                    *keys, count = line.strip('\n').split()
                    if reverse:
                        keys = reversed(keys)
                    *prior, posterior = keys
                    assert len(prior) + 1 == self.n
                    count = int(count)
                except:
                    raise Exception(f'Wrong format: expected {self.n} keys and a number. Got: "{line}"')
                else:
                    prior     = tuple(map(self.prune_prior, prior))
                    posterior = self.prune_posterior(posterior)
                    self[prior, posterior] += count
        return self
    
    def priorKeys(self):
        return {p for p,_ in self.keys()}
    def posteriorKeys(self):
        return {p for _,p in self.keys()}
    








class CrossEntropy:
    log_prob = 0
    num_elems = 0

    def feed(self, log_probability, num_elements = 1):
        self.log_prob += log_probability
        self.num_elems += num_elements

    def get(self):
        return -1/self.num_elems * self.log_prob
    

