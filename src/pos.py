from io import TextIOWrapper
from diccionari import getDiccionari, Pos, WordInfo
import utils
import re
from copy import copy
import xml.etree.ElementTree as ET

#CONTRACCIONS_INICIALS ='|'.join("l' d' m' t' s' n'".split())
#CONTRACCIONS_FINALS = '|'.join("'m -me 't -te 's -se 'l -la -lo 'ls -los -nos 'ns -vos -us -ho 'n -ne -hi".split())

RAW_DICCIONARI = getDiccionari()

aux_raw_dict = [x.word for x in RAW_DICCIONARI if "'" in x.word or '-' in x.word ]
CONTRACCIONS_INICIALS = '|'.join({w for w in aux_raw_dict if w[-1] in ('-', "'") and w.islower()})
CONTRACCIONS_FINALS   = '|'.join({w for w in aux_raw_dict if w[0] in ('-', "'") and w.islower()})


pos_list = ['A','C','D','F','I','N','P','R','S','V','Y','*','$']

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
            splitContraccions(word)
            for word in re.findall(
                f'{RE_NUM}|{RE_WORD}|{RE_PUNCTUATION}|\n(?!\n)',
                string
            )
        ),
    [])


DICCIONARI : dict[str, WordInfo] = utils.group(RAW_DICCIONARI, lambda info: info.word)

PUNTUACIO = {}

with open('diccionari/puntuacio.txt', 'r', encoding='utf-8') as f:
    for line in f:
        pos_, *tokens = f.read().split()
        for token in tokens:
            PUNTUACIO[token] = pos_
        


def categoriesPossibles(paraula:str, inici_frase:bool=False):
    if re.match(RE_PUNCTUATION+'$', paraula):
        return {PUNTUACIO.get(paraula, 'Fz')}
    elif re.match(RE_NUM+'$', paraula):
        return {'Zp' if paraula[-1] == '%' else 'Z'}
    elif paraula == '\n':
        return {'$'}
    
    info_list = copy(DICCIONARI[paraula])
    if inici_frase or not info_list: 
        info_list.extend(DICCIONARI[paraula.lower()])

    categories = {info.pos for info in info_list}

    #if paraula.lower() in DIES_SETMANA or paraula.lower() in MESOS_ANY or paraula in SEGLES:
    #              categories.add('W')

    if not categories and paraula[0].isupper():
        return {'NP0000'}

    return categories

def buscarCategoriesPossibles(string:str):
    assignacio = []
    inici_frase = True
    for paraula in splitWords(string):
        categories = categoriesPossibles(paraula, inici_frase)
        if not categories and '-' in paraula:
            assignacio.extend(buscarCategoriesPossibles(paraula.replace('-', ' - ')))
        else:
            if len(categories) == 1:
                (categoria,) = categories
            else:
                categoria = '?'
            assignacio.append([paraula, categoria, categories or {'?'}])
        inici_frase = (paraula == '.')
    return assignacio
    


            
#string = "Jo la vaig veure un dia clar, sota una llum que m'encegava i quan la vaig gosar mirar ella em tornava la mirada"

# Format simple (anàlisi morfològic escolar)

def printLiniaAssignacio(assignacio:list[tuple[str,str]], file:TextIOWrapper):
    for w, _ in assignacio:
        if w != '\n':
            print(w, end=' ', file=file)
    print(file=file)
    for w, c in assignacio:
        if w != '\n':
            print(c + ' '*(len(w)-1), end=' ', file=file)
    print(file=file)
    print(file=file)

def printAssignacio(assignacio:list[tuple[str,str]], file:TextIOWrapper, max_len_line=100):
    assignacio = list(assignacio)
    for paragraf_assignacio in utils.splitList(assignacio, sep_func=lambda x: x[0] == '\n'):
        if max_len_line:
            len_line = 0
            start = 0
            for i, (word, _) in enumerate(paragraf_assignacio):
                len_line += len(word) + 1
                if len_line > max_len_line:
                    printLiniaAssignacio(paragraf_assignacio[start:i], file)
                    start = i
                    len_line = 0
        printLiniaAssignacio(paragraf_assignacio[start:], file)


def readAssignacio(file:TextIOWrapper) -> list[WordInfo]:
    lines = file.readlines()
    tuples = []
    for i in range(0, len(lines)-2, 3):
        assert lines[i+2].strip('\n\r') == ''
        words = lines[i].split()
        pos = lines[i+1].split()
        assert len(words) == len(pos)
        if not words:
            tuples.append(('\n', '$'))
        else:
            tuples.extend(list(zip(words, pos)))
    return [WordInfo(word, None, pos) for word, pos in tuples]
        
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