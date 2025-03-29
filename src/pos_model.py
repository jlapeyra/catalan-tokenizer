from glob import glob
import distribution
import utils
import pos
import re
import numpy as np
import probability
from collections import defaultdict
from typing import Iterable
from pos import DICCIONARI, categoriesPossibles, splitWords
from copy import copy

def allPos(data:list[pos.WordInfo]=[]):
    pos_dicc = set(wi.pos for wi in pos.RAW_DICCIONARI)
    pos_punt = set(p for p in pos.PUNTUACIO.values())
    pos_data = set(wi.pos for wi in data)
    pos_others = {'W', 'Fz', 'Z', 'Zp'}
    pos_boundaries = {'$', '-'}
    return pos_dicc | pos_data | pos_punt | pos_others | pos_boundaries



class PosModel:

    def __init__(self, name, alpha=0.5, pos_list:Iterable=None, pos_len=1):
        if pos_list is None:
            pos_list = copy(pos.pos_list)
        else:
            pos_list = sorted(set(p[:pos_len] for p in pos_list))

        self.pos_len = pos_len
        self.idx2pos = pos_list
        self.pos2idx = {p:i for i,p in enumerate(pos_list)}
        self.num_pos = len(pos_list)

        N = self.num_pos
        count_back = np.zeros((N, N), dtype=np.int64)
        with open(f'model/{name}.{pos_len}pos.2gram.txt') as f:
            for line in f:
                k1, k2, num = line.split()
                if k1 not in self.pos2idx or k2 not in self.pos2idx:
                    continue
                k1 = self.pos2idx[k1]
                k2 = self.pos2idx[k2]
                num = int(num)
                count_back[k1, k2] = num

        count_fwd = count_back.T

        self.prob_cond_fwd = probability.distribution(count_fwd + alpha)
        self.prob_cond_back = probability.distribution(count_back + alpha)

        self.prob_a_priori = probability.distribution(np.ones(N, dtype=np.float64))

        count_by_type = defaultdict(lambda: np.zeros(N, dtype=np.int64))
        with open(f'model/{name}.{pos_len}pos.count.txt', encoding='utf-8') as f:
            for line in f:
                word, pos_, num = line.split()
                if k1 not in self.pos2idx or k2 not in self.pos2idx:
                    continue
                k = self.pos2idx[pos_]
                num = int(num)
                count_by_type[word][k] = num

        self.prob_by_type = dict()
        for word, count_ in count_by_type.items():
            self.prob_by_type[word] = probability.distribution(
                    count_ + 0.8*self.getCountArrayPos(self.getPosAllCase(word))
            )

    def getBoolArrayPos(self, pos_list:Iterable[str]):
        ret = np.zeros(self.num_pos, dtype=bool)
        for pos_ in pos_list:
            ret[self.pos2idx[pos_[:self.pos_len]]] = True
        return ret

    def getCountArrayPos(self, pos_list:Iterable[str]):
        ret = np.zeros(self.num_pos, dtype=np.int32)
        for pos_ in pos_list:
            ret[self.pos2idx[pos_[:self.pos_len]]] += 1
        return ret
    
    def getPosAllCase(self, word:str):
        return {
            info.pos[0] for info in 
            DICCIONARI[word] + DICCIONARI[word.upper()] + DICCIONARI[word.capitalize()]
        }

    def getSortedPos(self, arr_prob:np.ndarray):
        return sorted([
            (arr_prob[j], self.idx2pos[j]) for j in range(self.num_pos) if arr_prob[j]
        ], reverse=True)


    def getProbPosWord(self, token:str, inici_frase:bool):
        if token.lower() in self.prob_by_type:
            return self.prob_by_type[token.lower()]
        else:
            categories = categoriesPossibles(token, inici_frase)
            if not categories: 
                return probability.uniform(self.num_pos)
            return probability.distribution(self.getBoolArrayPos(categories))
        #prob *= getBoolArrayPos(categoriesPossibles(token, inici_frase))
        #if not np.any(prob): return copy(prob_a_priori)
        #return probability.distribution(prob)

    def predictPosProbDistribution(self, tokens):
        pos_vecs = []
        ini_frase = True
        for token in tokens:
            pos_vecs.append(self.getProbPosWord(token, ini_frase))
            ini_frase = (token == '.')

        boundary_pos_vec = self.getBoolArrayPos(['-'])


        for i in range(len(pos_vecs)):
            prev_pos_vec = pos_vecs[i-1] if i>0 else boundary_pos_vec
            pos_vecs[i] = probability.combination(pos_vecs[i], (self.prob_cond_fwd @ prev_pos_vec))
            #pos_vecs[i] = (prev_pos_vec @ prob_cond_fwd) * pos_vecs[i] / prob_a_priori
        #print()

        for i in reversed(range(len(pos_vecs))):
            prev_pos_vec = pos_vecs[i+1] if i<len(pos_vecs)-1 else boundary_pos_vec
            pos_vecs[i] = probability.combination(pos_vecs[i], (self.prob_cond_back @ prev_pos_vec))
            #pos_vecs[i] = (prev_pos_vec @ prob_cond_back) * pos_vecs[i] / prob_a_priori
        #print()

        return pos_vecs

    def posMax(self, vec):
        imax = max(range(self.num_pos), key=lambda i: vec[i])
        return self.idx2pos[imax]

    
    def print_pos(self, words, pos_vecs, / , limit=200):
        for w,probs in zip(words[:limit], pos_vecs):
            print(w, end=': ')
            for i,p in enumerate(probs):
                if p > 0:
                    print(f'{self.idx2pos[i]}:{p:.4f}', end=', ')
            print()
        print()




def train(name, data_file, format='line', n=2, pos_size=1):

    # N-gram of POS
    # probability of POS given previous/next POS

    ngram = distribution.NGram(n, ['-'])
    with open(data_file, 'r', encoding='utf-8') as f:
        match format:
            case 'insti': assignacio = pos.readAssignacio(f)
            case 'line': assignacio = [pos.WordInfo(*line.split()) for line in f]
            case _: raise ValueError(format)
    pos_list_full = [wi.pos[:pos_size] for wi in assignacio]
    for pos_list in utils.splitList(pos_list_full, seps=('Fp', '$', '.'), not_empty=True):
        ngram.feed(pos_list)
    with open(f'model/{name}.{pos_size}pos.{n}gram.txt', 'w') as f:
        ngram.save(f)


    # probability of POS given word

    probs = distribution.ConditionalDistribution()
    inici_frase = True
    for wi in assignacio:
        if not re.match(pos.RE_PUNCTUATION+'$', wi.word) and '_' not in wi.word:
            pos_ann = wi.pos[:pos_size]
            pos_dic = pos.categoriesPossibles(wi.word, inici_frase=inici_frase)
            pos_dic = [pos_[:pos_size] for pos_ in pos_dic]
            word = wi.word.lower()
            #if wi.pos[:2] != 'NP':
            #    word = word.lower()
            #if pos_dic and pos_ann not in pos_dic:
            #    print(f'WARNING: {word} {pos_ann} {pos_dic}')
            probs.add(word, pos_ann)
        inici_frase = (wi.pos in ('$', 'Fp'))
    for key in list(probs.keys()):
        if probs[key].total() <= 20:
            del probs[key]
    with open(f'model/{name}.{pos_size}pos.count.txt', 'w', encoding='utf-8') as f:
        probs.save(f)



if __name__ == '__main__':
    train(name='ancora', data_file='corpus/ancora-train.pos.txt', format='line', n=2, pos_size=1)
    train(name='ancora', data_file='corpus/ancora-train.pos.txt', format='line', n=2, pos_size=2)