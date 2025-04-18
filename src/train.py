import pos
import distribution
import utils
import re

class Trainer:
    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            self.data = [pos.WordInfo(*line.split()) for line in f]
        return self

    def train_pos_ngram(self, n:int, pos_limits:tuple[int,int]):
        prune = lambda wi: wi.pos[pos_limits[0]:pos_limits[0]]
        split = lambda wi: wi.pos in ('Fp', '$')
        ngram = distribution.NGram(n, '-', prune=prune)
        for pos_list in utils.splitList(self.data, sep_func=split, not_empty=True):
            ngram.feed(pos_list)
        return ngram


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
        return probs


if __name__ == '__main__':
    trainer = Trainer().load(f'data/ancora-train.pos.txt')
    trainer.train_pos_a_priori(pos_size=2).save()
    trainer.train_pos_ngram(n=3, pos_size=2)
    trainer.train_pos_ngram(n=2, pos_size=1) #...

