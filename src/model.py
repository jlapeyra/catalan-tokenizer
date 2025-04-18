from glob import glob
import distribution as distribution
import utils as utils
import pos
import re
import numpy as np
import probability
from collections import defaultdict
from typing import Iterable
from pos import DICCIONARI, splitWords
from copy import copy
from misc.numeros_i_dates import parse_date

def allPos(data:list[pos.WordInfo]=[]):
    pos_dicc = set(wi.pos for wi in pos.RAW_DICCIONARI)
    pos_punt = set(p for p in pos.PUNTUACIO.values())
    pos_data = set(wi.pos for wi in data)
    pos_others = {'W', 'Fz', 'Z', 'Zp'}
    pos_boundaries = {'$', '-'}
    return pos_dicc | pos_data | pos_punt | pos_others | pos_boundaries

class PosModel:
    def __init__(self, name, pos_len, alpha=0.5):
        pos_list = allPos()
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

    def predict(self, text):
        tokens = self.tokenize(text)
        pos_list = self.predictPos(tokens)
        token_entries = []
        for (token, entries), pos_ in zip(tokens, pos_list):
            feasible_entries = [entry for entry in entries if entry.pos[:self.pos_len] == pos_]
            if len(feasible_entries) > 1:
                print(f'WARNING: Multiple feasible entries {token} {pos_} {feasible_entries}')
            if feasible_entries:
                entry = feasible_entries[0]
            else:
                entry = pos.WordInfo(token, token, pos_)
            token_entries.append(entry)
        return self.__join_proper_nouns(entries)









    def getBoolArrayPos(self, pos_list:Iterable[str]):
        token_entries = np.zeros(self.num_pos, dtype=bool)
        for pos_ in pos_list:
            token_entries[self.pos2idx[pos_[:self.pos_len]]] = True
        return token_entries

    def getCountArrayPos(self, pos_list:Iterable[str]):
        token_entries = np.zeros(self.num_pos, dtype=np.int32)
        for pos_ in pos_list:
            token_entries[self.pos2idx[pos_[:self.pos_len]]] += 1
        return token_entries
    
    def getPosAllCase(self, word:str):
        return {
            info.pos[0] for info in 
            DICCIONARI[word] + DICCIONARI[word.upper()] + DICCIONARI[word.capitalize()]
        }

    def getSortedPos(self, arr_prob:np.ndarray):
        return sorted([
            (arr_prob[j], self.idx2pos[j]) for j in range(self.num_pos) if arr_prob[j]
        ], reverse=True)


    def getProbPosWord(self, token:tuple[str,list[pos.Entry]], inici_frase:bool):
        word, entry_list = token
        if word.lower() in self.prob_by_type:
            return self.prob_by_type[word.lower()]
        else:
            if not entry_list: 
                return probability.uniform(self.num_pos)
            pos_list = [e.pos for e in entry_list]
            return probability.distribution(self.getBoolArrayPos(pos_list))
        #prob *= getBoolArrayPos(dictionaryEntries(token, inici_frase))
        #if not np.any(prob): return copy(prob_a_priori)
        #return probability.distribution(prob)

    def tokenize(self, text:str) -> list[tuple[str,list[pos.Entry]]]:
        words = splitWords(text)
        tokens = []
        i = 0
        start_sentence = True
        while i < len(words):
            date = None
            token_size = 1
            for size in sorted(pos.LOCUCIONS.keys(), reverse=True):
                if i+size > len(words):
                    continue
                if tuple(words[i:i+size]) in pos.LOCUCIONS[size] \
                    or (words[i].lower(), *words[i+1:i+size]) in pos.LOCUCIONS[size]:
                    token_size = size
                    break
            date, size = parse_date(words[i:])
            if date:
                token_size = size
            
            token = '_'.join(words[i:i+token_size])
            i += token_size
            if date:
                entries = [pos.Entry(token, str(date), 'W')]
            else:
                entries = pos.dictionaryEntries(token, start=start_sentence)
            tokens.append((token, entries))

            start_sentence = token in ('.', '\n')
        return tokens

    def __join_proper_nouns(self, entries):
        result = []
        i = 0
        while i < len(entries):
            if entries[i].pos[:2] == 'NP':
                start = i
                while i + 1 < len(entries) and entries[i + 1].pos[:2] == 'NP':
                    i += 1
                token = '_'.join(entry.word  for entry in entries[start:i + 1])
                lemma = '_'.join(entry.lemma for entry in entries[start:i + 1])
                result.append(pos.WordInfo(token, lemma, 'NP'))
            else:
                result.append(entries[i])
            i += 1
        # n = len(ret)
        # i = n-1
        # while i >= 0 and ret[i].pos[:2] in ('SP', 'DA', 'CC'):
        #     i -= 1
        # if i >= 0 and ret[i].pos[:2] == 'NP':
        #     ret[i].word = '_'.join([ret[j].word for j in range(i, len(ret))] + [entry.word])
        #     ret[i].lemma = '_'.join([ret[j].lemma for j in range(i, len(ret))] + [entry.lemma])
        #     for j in range(i+1, n):
        #         ret.pop()
        #     continue
        return result



    

    def predictPos(self, tokens:list[tuple[str,list[pos.Entry]]]):
        pos_vecs = []
        ini_frase = True
        for token in tokens:
            pos_vecs.append(self.getProbPosWord(token, ini_frase))
            ini_frase = (token[0] == '.')

        boundary_pos_vec = self.getBoolArrayPos(['-'])

        prev_pos_vec = boundary_pos_vec
        for i in reversed(range(len(pos_vecs))):
            pos_vecs[i] = probability.combination(pos_vecs[i], (self.prob_cond_back @ prev_pos_vec))
            prev_pos_vec = pos_vecs[i]
        #print()

        prev_pos_vec = boundary_pos_vec
        picks = [None]*len(pos_vecs)
        for i in range(len(pos_vecs)):
            pos_vecs[i] = probability.combination(pos_vecs[i], (self.prob_cond_fwd @ prev_pos_vec))
            j = self.randomPick(pos_vecs[i])
            picks[i] = j
            pos_vecs[i] = np.zeros(self.num_pos, dtype=np.float64)
            pos_vecs[i][j] = 1.0
            prev_pos_vec = pos_vecs[i]
        #print()

        return [self.idx2pos[i] for i in picks]

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






if __name__ == '__main__':
    model = PosModel('ancora', pos_len=2)
    with open('data/minitrain/wiki.txt', encoding='utf-8') as in_:
        with open('data/minitrain/wiki.pos.txt', 'w', encoding='utf-8') as out:
            for line in in_.readlines():
                tokens = model.tokenize(line)
                pos_vecs = model.predictPos(tokens)
                for (t, options), p in zip(tokens, pos_vecs):
                    options = set(wi.pos[:2] for wi in options)
                    print(p, t, '\t', ','.join(options) if len(set(options)) > 1 else '', file=out)
                print(file=out)
                out.flush()