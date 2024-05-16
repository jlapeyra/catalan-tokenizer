from dataclasses import dataclass

@dataclass
class WordInfo:
    word:str
    lemma:str
    pos:str

def getDiccionari():
    with open('diccionari/diccionari.txt', 'r', encoding='utf-8') as f:
        return [WordInfo(*line.split()) for line in f]
    
