from collections import Counter, defaultdict
from io import TextIOWrapper
import math
import sys
from typing import Callable, Iterable
import numpy as np

ALPHA = 0.1

class Distribution(Counter):

    def add(self, item):
        self[item] += 1

    def __add__(self, other):
        if (isinstance(other, Counter)): 
            return Distribution(super().__add__(self, other))
        return Distribution({key:(value + other) for key,value in self.items()})
    
    def __div__(self, other):
        return Distribution({key:(value / other) for key,value in self.items()})
    
    def probability(self, key, alpha:float=ALPHA, num_keys:int=None):
        return (self[key] + alpha)/(self.total() + alpha*(num_keys or len(self.keys())))
    
    def logProbability(self, key, alpha:float=ALPHA, num_keys:int=None):
        return math.log(self.probability(key, alpha, num_keys), 2)

    def probabilityDistribution(self, alpha:float=ALPHA, num_keys:int=None):
        return Distribution({key: self.probability(key, alpha, num_keys) for key in self.keys()})
    
    def logProbabilityDistribution(self, alpha:float=ALPHA, num_keys:int=None):
        return Distribution({key: self.logProbability(key, alpha, num_keys) for key in self.keys()})

class ConditionalDistribution(defaultdict[object, Distribution]):

    def __init__(self) -> None:
        super(ConditionalDistribution, self).__init__(Distribution)

    def add(self, key1, key2):
        self[key1][key2] += 1

    def save(self, file:TextIOWrapper):
        for key1 in sorted(self):
            for key2 in sorted(self[key1]):
                count = self[key1][key2]
                print(key1, key2, count, file=file)
                
    def load(self, file:TextIOWrapper):
        for line in file.readlines():
            try:
                key1, key2, count = line.strip('\n').split()
                count = int(count)
            except:
                print(f'Wrong format: expected `key1* key2 num`. Got: "{line}"')
            else:
                self[key1][key2] = count
        return self

        
class NGram:

    def __init__(self, n:int, default) -> None:
        self.distributions = defaultdict(Distribution)
        self.n = n
        self.default = default

    def __forall_n_sequence(self, sequence:Iterable, action:Callable):
        preprocessed = self.default*(self.n-1) + sequence + self.default
        for i in range((self.n-1), len(preprocessed)):
            action(self.distributions[tuple(preprocessed[i-(self.n-1) : i])], preprocessed[i])


    def feed(self, sequence:Iterable):
        self.__forall_n_sequence(sequence, Distribution.add)

    def probability(self, sequence:Iterable, alpha:float=ALPHA, num_keys:int=None):
        prob = 1
        def update_prob(distribution:Distribution, key):
            nonlocal prob
            prob *= distribution.probability(key, alpha, num_keys)
        self.__forall_n_sequence(sequence, update_prob)
        return prob


    def logProbabity(self, sequence, alpha:float=ALPHA, num_keys:int=None):
        logprob = 0
        def update_logprob(distribution:Distribution, key):
            nonlocal logprob
            logprob += distribution.logProbability(key, alpha, num_keys)
        self.__forall_n_sequence(sequence, update_logprob)
        return logprob
    
    def save(self, file:TextIOWrapper):
        for key1 in sorted(self.distributions):
            for key2 in sorted(self.distributions[key1]):
                count = self.distributions[key1][key2]
                print(*key1, key2, count, file=file)
                
    def load(self, file:TextIOWrapper):
        for line in file.readlines():
            try:
                *key1, key2, count = line.strip('\n').split()
                count = int(count)
            except:
                print(f'Wrong format: expected `key1* key2 num`. Got: "{line}"')
            else:
                self.distributions[key1][key2] = count
        return self


class CrossEntropy:
    log_prob = 0
    num_elems = 0

    def feed(self, log_probability, num_elements = 1):
        self.log_prob += log_probability
        self.num_elems += num_elements

    def get(self):
        return -1/self.num_elems * self.log_prob
