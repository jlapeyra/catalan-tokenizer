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

class PosModel:
    idx2pos = copy(pos.pos_list)
    pos2idx = {p:i for i,p in enumerate(idx2pos)}
    num_pos = len(idx2pos)

    def __init__(self, name, alpha=0.5):
        N = self.num_pos
        count_back = np.zeros((N, N), dtype=np.int64)
        with open(f'model/{name}.1pos.2gram.txt') as f:
            for line in f:
                k1, k2, num = line.split()
                k1 = self.pos2idx[k1]
                k2 = self.pos2idx[k2]
                num = int(num)
                count_back[k1, k2] = num

        count_fwd = count_back.T

        self.prob_cond_fwd = probability.distribution(count_fwd + alpha)
        self.prob_cond_back = probability.distribution(count_back + alpha)

        assert np.array_equal(sum(count_back), sum(count_fwd))
        self.prob_a_priori = probability.distribution(np.ones(N, dtype=np.float64))

        count_by_type = defaultdict(lambda: np.zeros(N, dtype=np.int64))
        with open(f'model/{name}.1pos.count.txt', encoding='utf-8') as f:
            for line in f:
                word, pos_, num = line.split()
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
            ret[self.pos2idx[pos_]] = True
        return ret

    def getCountArrayPos(self, pos_list:Iterable[str]):
        ret = np.zeros(self.num_pos, dtype=np.int32)
        for pos_ in pos_list:
            ret[self.pos2idx[pos_]] += 1
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


    def getProbPosWord(self, paraula:str, inici_frase:bool):
        if paraula.lower() in self.prob_by_type:
            return self.prob_by_type[paraula.lower()]
        else:
            categories = categoriesPossibles(paraula, inici_frase)
            if not categories: 
                return probability.uniform(self.num_pos)
            return probability.distribution(self.getBoolArrayPos(categories))
        #prob *= getBoolArrayPos(categoriesPossibles(paraula, inici_frase))
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
        print()

        for i in reversed(range(len(pos_vecs))):
            prev_pos_vec = pos_vecs[i+1] if i<len(pos_vecs)-1 else boundary_pos_vec
            pos_vecs[i] = probability.combination(pos_vecs[i], (self.prob_cond_back @ prev_pos_vec))
            #pos_vecs[i] = (prev_pos_vec @ prob_cond_back) * pos_vecs[i] / prob_a_priori
        print()

def posMax(vec):
    imax = max(range(PosModel.num_pos), key=lambda i: vec[i])
    return PosModel.idx2pos[imax]

    
def print_pos(words, pos_vecs, / , limit=200):
    for w,probs in zip(words[:limit], pos_vecs):
        print(w, end=': ')
        for i,p in enumerate(probs):
            if p > 0:
                print(f'{PosModel.idx2pos[i]}:{p:.4f}', end=', ')
        print()
    print()



def train():

    # 2-gram of POS
    # probability of POS given previous/next POS

    n = 2
    pos_size = 2
    ngram = distribution.NGram(n, ['-'])
    for filename in glob('corpus/train.pos.txt'):
        #dataset = sys.argv[1]
        with open(filename, 'r', encoding='utf-8') as f:
            assignacio = pos.readAssignacio(f)
        pos_list_full = [pos for _, pos in assignacio]
        for pos_list in utils.splitList(pos_list_full, seps=('Fp', '$'), not_empty=True):
            ngram.feed(pos_list)
    with open(f'model/pos{pos_size}.{n}gram.txt', 'w') as f:
        ngram.save(f)


    # probability of POS given word

    probs = distribution.ConditionalDistribution()
    for fn in glob('corpus/train.pos.txt'):
        with open(fn, 'r', encoding='utf-8') as f:
            assignacio = pos.readAssignacio(f)
        for i, (paraula, pos_) in enumerate(assignacio):
            if not re.match(pos.RE_PUNCTUATION+'$', paraula.lower()):
                pos_pos = pos.categoriesPossibles(paraula)
                if pos_pos and pos_ not in pos_pos:
                    print(f'WARNING: {paraula} {pos_} {pos_pos}', \
                          '\t'+' '.join(w for w,p in assignacio[i-5:i+5]))
                probs.add(paraula.lower(), pos_)
    for key in list(probs.keys()):
        if probs[key].total() < 8:
            del probs[key]
    with open(f'model/pos{pos_size}.count.txt', 'w', encoding='utf-8') as f:
        probs.save(f)



if __name__ == '__main__':
    main()