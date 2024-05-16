from diccionari import getDiccionari
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
    
    


'''def splitContraccions(word:str):
    if "'" not in word and "-" not in word:
        return [paraula]
    found = True
    contraccions_fi = []
    while found:
        found = False
        for contraccio in CONTRACCIONS_FINALS:
            if word.endswith(contraccio):
                word = word.removesuffix(contraccio)
                contraccions_fi.append(word)
    found = True
    contraccions_ini = []
    while found:
        found = False
        for contraccio in CONTRACCIONS_INICIALS:
            if word.startswith(contraccio):
                word = word.removeprefix(contraccio)
                contraccions_ini.append(word)
    return contraccions_ini + [paraula] + list(reversed(contraccions_fi))'''


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
    if categoria_posterior == 'N' or categoria_posterior == 'D':
        if 'D' in opcions:
            return 'D'
        elif 'S' in opcions:
            return 'S'
    elif categoria_posterior == 'V':
        if 'P' in opcions:
            return 'P'
    return '?'


def assignarCategoria(string:str):
    assignacio = []
    for paraula in splitWords(string):
        info_list = DICCIONARI[paraula] or DICCIONARI[paraula.lower()] or DICCIONARI[paraula.upper()] or DICCIONARI[paraula.capitalize()]
        categories = sorted(utils.group(info_list, lambda info: info.pos[0]))
        if len(categories) == 1:
            categoria = categories[0]
        else:
            categoria = '?'
        assignacio.append([paraula, categoria, categories])

    for i in reversed(range(len(assignacio))):
        paraula, categoria, categories = assignacio[i]
        if categoria == '?' and i < len(assignacio[i]):
            assignacio[i][1] = triaCategoria(categories, assignacio[i+1][1])
    return assignacio
            
string = "Jo la vaig veure un dia clar sota una llum que m'encegava i quan la vaig gosar mirar ella em tornava la mirada"

for w, _, _ in assignarCategoria(string):
    print(w, end=' ')
print()
for w, c, _ in assignarCategoria(string):
    print(c + ' '*(len(w)-1), end=' ')