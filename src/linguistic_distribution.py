from distribution import Distribution, ConditionalDistribution, NGram, CoOccurrences
from pos import WordInfo
import numpy as np
import itertools
import probability
from utils import id

ALL = slice(None)

def slicePos(wi:WordInfo, slice:slice):
    return wi.pos[slice]

def slicePosFunc(slice:slice):
    return lambda wi: slicePos(wi, slice)

def idxs(arr):
    return {x:i for i,x in enumerate(arr)}

def randomPick(probs:np.ndarray):
    assert np.isclose(np.sum(probs), 1)
    probs = np.cumsum(probs)
    r = np.random.rand()
    for i in range(len(probs)):
        if probs[i] >= r:
            return i
    return len(probs)-1

POS_DEFAULT = '-'

class PosNGram(NGram):
    def __init__(self, n, slice=ALL, alpha=0.5, reverse=False):
        self.alpha = alpha
        self.reverse = reverse
        super().__init__(n, POS_DEFAULT, func=slicePosFunc(slice))

    def load(self, filename):
        return super().load(filename, self.reverse)
    
    def predict(self, pos_list, pos_vecs):
        k = self.n-1
        ret = [POS_DEFAULT]*k
        for i, old_vec in enumerate(pos_vecs):
            ngram_vec = self[tuple(ret[i-k:i])].probabilityDistribution(self.alpha, len(pos_list))
            new_vec = probability.combination(old_vec, ngram_vec)
            pick = randomPick(new_vec)
            ret.append(pos_list[pick])
        ret = ret[k:]
        assert len(ret) == len(pos_vecs)
        return ret


class Pos2Gram(PosNGram):
    def __init__(self, slice=ALL, alpha=0.5, reverse=False):
        super().__init__(2, slice, alpha, reverse)

    def prob_matrix(self, pos_list):
        ret:np.ndarray = np.zeros((len(pos_list), len(pos_list)))
        for i, x in enumerate(pos_list):
            for j, y in enumerate(pos_list):
                ret[i,j] = self[(x,)][y]
        return probability.distribution(ret + self.alpha)
    
    def boundary_pos_vec(self, pos_list:list):
        assert self.default in pos_list
        vec = np.zeros(len(pos_list))
        vec[pos_list.index(self.default)] = 1
        return vec

    def updatePosVecs(self, pos_list, pos_vecs):
        matrix = self.prob_matrix(pos_list)
        prev_pos_vec = self.boundary_pos_vec()
        r = reversed if self.reverse else id
        for i in r(range(len(pos_vecs))):
            pos_vecs[i] = probability.combination(pos_vecs[i], (matrix @ prev_pos_vec))
            prev_pos_vec = pos_vecs[i]

class PosCount(ConditionalDistribution):
    def __init__(self):
        super().__init__()