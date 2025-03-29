import pos
from collections import defaultdict
from glob import glob
import os
import pos


def llista():
    locucions = defaultdict(set[pos.WordInfo])

    for wi in pos.loadAncora('train'):
        if '_' in wi.word and '_' != wi.word:
            words = wi.word.split('_')
            if not wi.pos.startswith('NP') and words[0].istitle():
                wi.word = '_'.join((words[0].lower(), *words[1:]))
            locucions[wi.pos[0]].add(wi)

    for pos_type, locs in locucions.items():
        #print(pos_type, len(locs))
        with open(f'locucions/loc-{pos_type}.txt', 'w', encoding='utf-8') as f:
            for loc in sorted(locs, key=lambda loc: (loc.pos, loc.lemma, loc.word)):
                print(loc.pos, loc.lemma, loc.word, file=f)

def simplify_pos(loc_pos, pos_list):
    if not pos_list:
        return pos_list
    for i in range(len(loc_pos), min(1, len(loc_pos)//2-1), -1):
        ret = []
        for pos_ in pos_list:
            if pos_[:i] == loc_pos[:i]:
                ret.append(pos_)
            if ret:
                return ret
    return pos_list



def annotate_pos(include=None, exclude=('Z', 'W')):
    for fn in glob('locucions/loc-*.txt'):
        basename = os.path.basename(fn)
        key = basename[4]
        if include and key not in include:
            continue
        if exclude and key in exclude:
            continue
        if basename in ('loc-Z.txt', 'loc-W.txt'):
            continue
        with open(fn, 'r', encoding='utf-8') as in_:
            with open(f'locucions/pos-v2-{basename}', 'w', encoding='utf-8') as out:
                for line in in_:
                    pos_, lemma, word = line.split()
                    print(word)
                    print(line.strip('\n'), file=out)
                    propi = pos_[:2] != 'NP'
                    ini = True
                    for word in word.split('_'):
                        print(word, end=': ', file=out)
                        pos_list = pos.categoriesPossibles(word, inici_frase=ini and not propi)
                        pos_list = simplify_pos(pos_, pos_list)
                        print(*pos_list, sep=', ', file=out)
                        ini = False
                    print(file=out)



                    