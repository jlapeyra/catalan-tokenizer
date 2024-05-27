from diccionari import getDiccionari, Pos
import utils
import re

CONTRACCIONS_INICIALS ='|'.join("l' d' m' t' s' n'".split())
CONTRACCIONS_FINALS = '|'.join("'m -me 't -te 's -se 'l -la -lo -los -nos -vos -us 'ns 'n".split())


def splitContraccions(word:str):
    if not ("'" in word or "-" in word):
        return [word]
    contr_ini = []
    contr_fi = []
    while match := re.search('({})$'.format(CONTRACCIONS_FINALS), word):
        word = word[:match.start()]
        contr_fi.insert(0, match.group())
    while match := re.match('({})'.format(CONTRACCIONS_INICIALS), word):
        word = word[match.end():]
        contr_ini.append(match.group())
    return contr_ini + [word] + contr_fi
    
    

RE_WORD = r"[\w·\-']+"
RE_PUNCTIATION = r'(?:[,;:.()?!"]|\.\.\.)'

def splitWords(string):
    return sum((
            splitContraccions(word)
            for word in re.findall(
                f'{RE_WORD}|{RE_PUNCTIATION}',
                string
            )
        ),
    [])

#"Jo la vaig veure un dia clar sota una llum que m'encegava i quan la vaig gosar mirar ella em tornava la mirada"


DICCIONARI = utils.group(getDiccionari(), lambda info: info.word)


def triaCategoria(opcions, categoria_posterior):
    if categoria_posterior in (Pos.NOM, Pos.DETERMINANT):
        if   Pos.DETERMINANT in opcions: 
            return Pos.DETERMINANT
        elif Pos.PREPOSICIO  in opcions: 
            return Pos.PREPOSICIO
    elif categoria_posterior == Pos.VERB:
        if Pos.PRONOM in opcions: 
            return Pos.PRONOM
    return '?'


def assignarCategoria(string:str):
    assignacio = []
    for paraula in splitWords(string):
        if re.match(RE_PUNCTIATION+'$', paraula):
            categories = ['.']
        else:
            info_list = DICCIONARI[paraula] or DICCIONARI[paraula.lower()] or DICCIONARI[paraula.upper()] or DICCIONARI[paraula.capitalize()]
            categories = sorted(utils.group(info_list, lambda info: info.pos[0]))
        if len(categories) == 1:
            categoria = categories[0]
        else:
            categoria = '?'
        assignacio.append([paraula, categoria, categories])

    for i in reversed(range(len(assignacio))):
        paraula, categoria, categories = assignacio[i]
        if categoria == '?' and i+1 < len(assignacio):
            assignacio[i][1] = triaCategoria(categories, assignacio[i+1][1])
    return assignacio
            
string = "Jo la vaig veure un dia clar, sota una llum que m'encegava i quan la vaig gosar mirar ella em tornava la mirada"


def assignPosAndPrint(string, file):
    for w, _, _ in assignarCategoria(string):
        print(w, end=' ', file=file)
    print(file=file)
    for w, c, _ in assignarCategoria(string):
        print(c + ' '*(len(w)-1), end=' ', file=file)
    print(file=file)
    print(file=file)

if __name__ == '__main__':
    count = 0
    with open('data/catalunya.wiki.pos.txt', 'w', encoding='utf-8') as out:
        with open('data/catalunya.wiki.txt', 'r', encoding='utf-8') as f:
            for paragraf in f:
                count += 1
                while paragraf:
                    if len(paragraf) < 120:
                        linia = paragraf
                        paragraf = ''
                    else:
                        i = paragraf[:120].rfind(' ')
                        linia = paragraf[:i]
                        paragraf = paragraf[i:]
                    assignPosAndPrint(linia, out)
                if count >= 10:
                    break