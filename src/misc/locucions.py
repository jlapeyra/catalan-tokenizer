import pos
from collections import defaultdict, Counter
from glob import glob
import os
import pos
import utils as utils


def llista_corpus():
    locucions_list = defaultdict(list)

    for wi in pos.loadAncora('train'):
        if '_' in wi.word and '_' != wi.word:
            words = wi.word.split('_')
            if not wi.pos.startswith('NP') and words[0].istitle():
                wi.word = '_'.join((words[0].lower(), *words[1:]))
            locucions_list[wi.pos[0]].append(wi)

    locucions = {k:Counter(l) for k,l in locucions_list.items()}
    locucions:dict[str,Counter[pos.WordInfo]]

    for pos_type, locs in locucions.items():
        #print(pos_type, len(locs))
        with open(f'locucions/corpus-ancora/loc-{pos_type}.txt', 'w', encoding='utf-8') as f:
            for loc, count in sorted(locs.items(), key=lambda x: (-x[1], x[0])):
                print(count, loc.dump(), file=f)


def possessius():
    GENERES = 'MF'
    NOMBRES = 'SP'
    GN = [g+n for g in GENERES for n in NOMBRES]
    determinants = {gn:[] for gn in GN}
    pronoms = {gn:[] for gn in GN}
    with open('locucions/possessius.txt', 'r', encoding='utf-8') as f:
        for line in f:
            wi = pos.WordInfo(*line.split())
            genere = wi.pos[3]
            nombre = wi.pos[4]
            generes = genere if genere in GENERES else GENERES
            nombres = nombre if nombre in NOMBRES else NOMBRES
            conjunt = determinants if wi.pos[0] == 'D' else pronoms
            for g in generes:
                for n in nombres:
                    conjunt[g+n].append(wi)
    locucions:list[pos.WordInfo] = []
    for gn in GN:
        for det in determinants[gn]:
            for pro in pronoms[gn]:
                det:pos.WordInfo
                pro:pos.WordInfo
                if det.lemma == 'es' and pro.word.endswith('eua') or pro.word.endswith('eues'):
                    continue
                word = det.word + '_' + pro.word
                lemma = det.lemma + '_' + pro.lemma
                pos_pro = pro.pos
                pos_det = 'DP' + pos_pro[2] + gn + pos_pro[5]
                locucions.append(pos.WordInfo(word, lemma, pos_det))
                locucions.append(pos.WordInfo(word, lemma, pos_pro))
    with open('locucions/loc-possessius.txt', 'w', encoding='utf-8') as f:
        for wi in sorted(locucions):
            print(wi.dump(), file=f)

def locucions_al_diccionari():
    locucions = set()
    for pos_type, min_count in [
        ('S', 15),
        ('R', 20),
        ('C', 10),
    ]:
        with open(f'locucions/corpus-ancora/loc-{pos_type}.txt', 'r', encoding='utf-8') as f:
            for line in f:
                count, *wi_data = line.split()
                if int(count) < min_count:
                    continue
                wi = pos.WordInfo(*wi_data)
                locucions.add(wi)
    for fn in glob('locucions/wictionary/*.txt'):
        pos_ = os.path.basename(fn).split('-')[1].split('.')[0]
        with open(fn, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                word = line.strip()
                lemma = word
                locucions.add(pos.WordInfo(word, lemma, pos_))
    with open('locucions/loc-possessius.txt', 'r', encoding='utf-8') as f:
        for line in f:
            locucions.add(pos.WordInfo(*line.split()))

    # Remove erratic redundandness (prepotitive locucions recorded as other locutions)
    prep_lemma = {wi.lemma for wi in locucions if wi.pos.startswith('S')}
    locucions = {wi for wi in locucions if wi.pos.startswith('S') or wi.lemma not in prep_lemma}

    with open('diccionari/locucions.txt', 'w', encoding='utf-8') as f:
        for loc in sorted(locucions):
            print(loc.dump(), file=f)
            
locucions_al_diccionari()

# def simplify_pos(loc_pos, pos_list):
#     if not pos_list:
#         return pos_list
#     for i in range(len(loc_pos), min(1, len(loc_pos)//2-1), -1):
#         ret = []
#         for pos_ in pos_list:
#             if pos_[:i] == loc_pos[:i]:
#                 ret.append(pos_)
#             if ret:
#                 return ret
#     return pos_list

# def annotate_pos(include=None, exclude=('Z', 'W')):
#     for fn in glob('locucions/loc-*.txt'):
#         basename = os.path.basename(fn)
#         key = basename[4]
#         if include and key not in include:
#             continue
#         if exclude and key in exclude:
#             continue
#         if basename in ('loc-Z.txt', 'loc-W.txt'):
#             continue
#         with open(fn, 'r', encoding='utf-8') as in_:
#             with open(f'locucions/pos-v2-{basename}', 'w', encoding='utf-8') as out:
#                 for line in in_:
#                     pos_, lemma, word = line.split()
#                     print(word)
#                     print(line.strip('\n'), file=out)
#                     propi = pos_[:2] != 'NP'
#                     ini = True
#                     for word in word.split('_'):
#                         print(word, end=': ', file=out)
#                         pos_list = pos.dictionaryEntries(word, inici_frase=ini and not propi)
#                         pos_list = simplify_pos(pos_, pos_list)
#                         print(*pos_list, sep=', ', file=out)
#                         ini = False
#                     print(file=out)



                    