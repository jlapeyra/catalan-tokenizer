from dataclasses import dataclass

@dataclass
class WordInfo:
    word:str
    lemma:str
    pos:str

def getDiccionari():
    print('getDiccionari...')
    with open('diccionari/diccionari.txt', 'r', encoding='utf-8') as f:
        r = [WordInfo(*line.split()) for line in f]
    print('getDiccionari done')
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
    ENUMERACIO = 'F'
    PUNTUACIO = '.'
    
