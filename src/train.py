import pos
import distribution
import utils
import re

class Trainer:
    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self.data = [pos.WordInfo(*line.split()) for line in f]

    def train_pos_ngram(self, n:int, pos_limits:tuple[int,int]):
        prune = lambda wi: wi.pos[pos_limits[0]:pos_limits[0]]
        split = lambda wi: wi.pos in ('Fp', '$')
        ngram = distribution.NGram(n, '-', prune=prune)
        for pos_list in utils.splitList(self.data, sep_func=split, not_empty=True):
            ngram.feed(pos_list)


    def train_pos_a_priori(self, pos_size):
        # probability of POS given word
        probs = distribution.ConditionalDistribution()
        inici_frase = True
        for wi in self.data:
            if wi.pos[0].isalpha() and wi.pos[0] != 'F':
                pos_ann = wi.pos[:pos_size]
                pos_dic = pos.dictionaryEntries(wi.word, inici_frase=inici_frase)
                pos_dic = [pos_[:pos_size] for pos_ in pos_dic]
                word = wi.word.lower()
                probs.add(word, pos_ann)
            inici_frase = (wi.pos in ('$', 'Fp'))
        
        for key in list(probs.keys()):
            if probs[key].total() <= 20:
                del probs[key]


# with open(f'model/{name}.{pos_size}pos.count.txt', 'w', encoding='utf-8') as f:
#     probs.save(f)
# with open(f'model/{name}.{pos_size}pos.{n}gram.txt', 'w') as f:
#     ngram.save(f)


