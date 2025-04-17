from io import TextIOWrapper
import sys
from warnings import deprecated
from diccionari import WordInfo
from pos import splitWords, dictionaryEntries
import utils

def buscarCategoriesPossibles(string:str):
    assignacio = []
    start = True
    for word in splitWords(string):
        categories = dictionaryEntries(word, start)
        if not categories and '-' in word:
            assignacio.extend(buscarCategoriesPossibles(word.replace('-', ' - ')))
        else:
            if len(categories) == 1:
                (categoria,) = categories
            else:
                categoria = '?'
            assignacio.append([word, categoria, categories or {'?'}])
        start = (word == '.')
    return assignacio
    


            
#string = "Jo la vaig veure un dia clar, sota una llum que m'encegava i quan la vaig gosar mirar ella em tornava la mirada"

# Format simple (anàlisi morfològic escolar)

@deprecated
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

@deprecated
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


@deprecated
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


if __name__ == '__main__':
    dataset = sys.argv[1]
    with open(f'corpus/{dataset}.pos.txt', 'w', encoding='utf-8') as out:
        with open(f'corpus/{dataset}.txt', 'r', encoding='utf-8') as in_:
            count = 0
            for paragraf in in_:
                #printAssignacio(assignarCategories(paragraf), out)
                count += 1
                #if count > 20:
                #    break
                #print('\n\n\n', end='', file=out) #indica canvi de paràgraf
