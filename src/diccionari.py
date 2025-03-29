from dataclasses import dataclass

@dataclass
class WordInfo:
    word:str
    lemma:str
    pos:str

    def dump(self):
        return f'{self.word.replace(' ', '_')} {self.lemma.replace(' ', '_')} {self.pos}'
    
    def __tuple__(self):
        return (self.word, self.lemma, self.pos)
    def __hash__(self):
        return hash(self.__tuple__())
    def __lt__(self, other:'WordInfo'):
        return self.__tuple__() < other.__tuple__()


class Entry(WordInfo):
    pass

def getDiccionari():
    #print('getDiccionari...')
    with open('diccionari/diccionari.txt', 'r', encoding='utf-8') as f:
        r = [WordInfo(*line.split()) for line in f]
    #print('getDiccionari done')
    return r
    
class Pos:
    NOM = 'N'
    ADJECTIU = 'A'
    DETERMINANT = 'D'
    PREPOSICIO = 'S'
    VERB = 'V'
    ADVERBI = 'R'
    PRONOM = 'P'
    CONJUNCIO = 'C'
    ABREVIACIO = 'Y'
    PUNTUACIO = 'F'
    NUMERO = 'Z'
    DATA = 'W'
    
