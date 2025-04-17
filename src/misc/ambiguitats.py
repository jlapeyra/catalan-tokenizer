import utils as utils
from diccionari import getDiccionari

ambiguitats = [0]*6

diccionari = getDiccionari()
info_by_word = utils.group(diccionari, lambda info: info.word)
with open('diccionari/ambiguitats-lema.txt', 'w', encoding='utf-8') as f:
    for word, info_list in info_by_word.items():
        if len(info_list) == 0:
            continue
        lemmas = set(info.lemma for info in info_list)
        if len(lemmas) > 1:
            print(word, ':', ','.join(lemmas), file=f)
        for i in range(6):
            if len(set((info.pos[:i], info.lemma) for info in info_list)) > 1:
                ambiguitats[i] += 1

total = len(diccionari)
for i in range(6):
    print(i, ':', '{:.2d} % ({})'.format(ambiguitats[i]/total*100, ambiguitats[i]))


        
