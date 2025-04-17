from io import TextIOWrapper
from warnings import deprecated
from diccionari import getDiccionari, getLocucions, Pos, WordInfo, Entry
import utils as utils
import re
from copy import copy
import xml.etree.ElementTree as ET

#CONTRACCIONS_INICIALS ='|'.join("l' d' m' t' s' n'".split())
#CONTRACCIONS_FINALS = '|'.join("'m -me 't -te 's -se 'l -la -lo 'ls -los -nos 'ns -vos -us -ho 'n -ne -hi".split())

RAW_DICCIONARI = getDiccionari()
RAW_LOCUCIONS = getLocucions()

aux_raw_dict = [x.word for x in RAW_DICCIONARI if "'" in x.word or '-' in x.word ]
CONTRACCIONS_INICIALS = '|'.join({w for w in aux_raw_dict if w[-1] in ('-', "'") and w.islower()})
CONTRACCIONS_FINALS   = '|'.join({w for w in aux_raw_dict if w[0] in ('-', "'") and w.islower()})

DICCIONARI : dict[str, WordInfo] = utils.group(RAW_DICCIONARI+RAW_LOCUCIONS, lambda info: info.word)
LOCUCIONS : dict[str, WordInfo] = utils.group([
    tuple(wi.word.split('_')) for wi in RAW_LOCUCIONS], 
    len,
    container=set
)

PUNTUACIO = {}
with open('diccionari/puntuacio.txt', 'r', encoding='utf-8') as f:
    for line in f:
        pos_, *tokens = f.read().split()
        for token in tokens:
            PUNTUACIO[token] = pos_

def splitContraccions(word:str):
    if not ("'" in word or "-" in word):
        return [word]
    contr_ini = []
    contr_fi = []
    while match := re.search('({})$'.format(CONTRACCIONS_FINALS), word, flags=re.IGNORECASE):
        word = word[:match.start()]
        contr_fi.insert(0, match.group())
    while match := re.match('({})'.format(CONTRACCIONS_INICIALS), word, flags=re.IGNORECASE):
        word = word[match.end():]
        contr_ini.append(match.group())
    return contr_ini + [word] + contr_fi
    
    

RE_WORD = r"(\w[\w·\-']*\w|\w)"
RE_NUM = r'((\d([\., ]\d)*|\d)(\w*|%))'
#RE_PUNCTUATION = r'([,;:.()?!"]|\.\.\.)'
RE_PUNCTUATION = r'(\.\.\.|[,;:.()?!"%_]|((?<=\s)|^)[^\w\s]|[^\w\s](?=\s|$))'
RE_NUMEROS_ROMANS = r'([IVXLCDM]+)'


def splitWords(string:str) -> list[str]:
    return sum((
            splitContraccions(m.group(0))
            for m in re.finditer(
                f'{RE_NUM}|{RE_WORD}|{RE_PUNCTUATION}|\n(?!\n)',
                string
            )
        ),
    [])



        


def dictionaryEntries(word:str, start:bool=False):
    if re.match(RE_PUNCTUATION+'$', word):
        return {Entry(word, word, PUNTUACIO.get(word, 'Fz'))}
    elif re.match(RE_NUM+'$', word):
        return {Entry(word, word, 'Zp' if word[-1] == '%' else 'Z')}
    elif word == '\n':
        return {Entry('\n', '\n', '$')}
    
    entries = set(DICCIONARI[word])
    if start or word.isupper(): 
        entries.union(DICCIONARI[word.lower()])

    #if word.lower() in DIES_SETMANA or word.lower() in MESOS_ANY or word in SEGLES:
    #              categories.add('W')

    if not entries and word[0].isupper():
        return {Entry(word, word, 'NP0000')}

    return entries


        
# Format ancora (XML)

def readTagsFromXML(filename:str) -> list[WordInfo]:
    ret = []
    with open(filename, 'r', encoding='utf-8') as file:
        tree = ET.parse(file)
    for element in tree.iter():
        if 'wd' in element.attrib:
            wi = WordInfo(element.attrib['wd'], element.attrib['lem'], element.attrib.get('pos', element.tag))
            wi.pos = wi.pos.title() if wi.pos[0] in 'fz' else wi.pos.upper()
            ret.append(wi)
    return ret

def loadAncora(set:str) -> list[WordInfo]:
    with open(f'corpus/ancora-{set}.pos.txt', 'r', encoding='utf-8') as file:
        r = [WordInfo(*line.split()) for line in file]
    return r
    
if __name__ == '__main__':
    import glob, random
    
    files = glob.glob('ancora/ancora-2.0/*/*.tbf.xml')
    random.shuffle(files)
    split = int(len(files)*0.7)
    train = files[:split]
    test = files[split:]

    with open('corpus-pos/ancora-train.pos.txt', 'w', encoding='utf-8') as f:
        for fn in train:
            for wi in readTagsFromXML(fn):
                print(wi.dump(), file=f)
            print('_ _ $', file=f)
    with open('corpus-pos/ancora-test.pos.txt', 'w', encoding='utf-8') as f:
        for fn in test:
            for wi in readTagsFromXML(fn):
                print(wi.dump(), file=f)
            print('_ _ $', file=f)