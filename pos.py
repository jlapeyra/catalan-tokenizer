from io import TextIOWrapper
from diccionari import getDiccionari, Pos
import utils
import re
from copy import copy

#CONTRACCIONS_INICIALS ='|'.join("l' d' m' t' s' n'".split())
#CONTRACCIONS_FINALS = '|'.join("'m -me 't -te 's -se 'l -la -lo 'ls -los -nos 'ns -vos -us -ho 'n -ne -hi".split())

RAW_DICCIONARI = getDiccionari()

CONTRACCIONS_INICIALS = '|'.join({x.word for x in RAW_DICCIONARI if x.word[-1:] in ('-', "'") and x.word.islower()})
CONTRACCIONS_FINALS = '|'.join({x.word for x in RAW_DICCIONARI if x.word[:1] in ('-', "'") and x.word.islower()})


pos_list = ['A','C','D','F','I','N','P','R','S','V','Y','.',',','-','*','?','$']

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
    
    

RE_WORD = r"(?:\w[\w·\-']*\w|\w)"
RE_NUM = r'(?:\d[\d\.\,]*\d\w*|\d\w*)'
#RE_PUNCTUATION = r'(?:[,;:.()?!"]|\.\.\.)'
RE_PUNCTUATION = r'(?:\.\.\.|[,;:.()?!"%_]|(?:(?<=\s)|^)[^\w\s]|[^\w\s](?=\s|$))'


def splitWords(string:str) -> list[str]:
    return sum((
            splitContraccions(word)
            for word in re.findall(
                f'{RE_NUM}|{RE_WORD}|{RE_PUNCTUATION}|\n(?!\n)',
                string
            )
        ),
    [])

#"Jo la vaig veure un dia clar sota una llum que m'encegava i quan la vaig gosar mirar ella em tornava la mirada"


DICCIONARI = utils.group(RAW_DICCIONARI, lambda info: info.word)


# def triaCategoria(opcions, categoria_posterior, categoria_anterior):
#     if categoria_posterior in (Pos.NOM, Pos.DETERMINANT):
#         if Pos.DETERMINANT in opcions: 
#             return Pos.DETERMINANT
#         elif Pos.PREPOSICIO  in opcions: 
#             return Pos.PREPOSICIO
#     elif categoria_posterior == Pos.VERB:
#         if Pos.PRONOM in opcions: 
#             return Pos.PRONOM
#     if categoria_anterior == Pos.DETERMINANT:
#         if Pos.NOM in opcions:
#             return Pos.NOM
#     return '?'

# def assignarCategories(string:str):
#     assignacio = buscarCategoriesPossibles(string)

#     retorn = []
#     for i in reversed(range(len(assignacio))):
#         paraula, categoria, categories = assignacio[i]
#         if categoria == '?':
#             categoria_posterior = categoria_anterior = None
#             if i+1 < len(assignacio):
#                 categoria_posterior = assignacio[i+1][1]
#             if i-1 >= 0:
#                 categoria_anterior = assignacio[i-1][1]
#             categoria = triaCategoria(categories, categoria_posterior, categoria_anterior)
#         retorn.append([paraula, categoria])
#     return list(reversed(retorn))

def categoriesPossibles(paraula:str, inici_frase:bool=False):
    if re.match(RE_PUNCTUATION+'$', paraula):
        return {'.' if paraula == '.' else ','}
    elif paraula == '\n':
        return {'$'}
    
    info_list = copy(DICCIONARI[paraula])
    if inici_frase or not info_list: 
        info_list.extend(DICCIONARI[paraula.lower()])

    categories = {info.pos[0] for info in info_list}

    if re.match(RE_NUM+'$', paraula):
        categories.update({Pos.ADJECTIU} if paraula[-1].isalpha() else {Pos.DETERMINANT, Pos.NOM})

    if paraula[0].isupper() and not categories: #and not inici_frase
        #categories.add('*')
        return {'*'}

    return categories or {'?'}

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
            assignacio.append([paraula, categoria, categories])
        inici_frase = (paraula == '.')
    return assignacio
    


            
#string = "Jo la vaig veure un dia clar, sota una llum que m'encegava i quan la vaig gosar mirar ella em tornava la mirada"


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

def readAssignacio(file:TextIOWrapper) -> list[tuple[str, str]]:
    lines = file.readlines()
    retorn = []
    for i in range(0, len(lines)-2, 3):
        assert lines[i+2].strip('\n\r') == ''
        words = lines[i].split()
        pos = lines[i+1].split()
        assert len(words) == len(pos)
        if not words:
            retorn.append(('\n', '$'))
        else:
            retorn.extend(list(zip(words, pos)))
    return retorn
        


    