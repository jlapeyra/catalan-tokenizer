import pos
from collections import defaultdict

locucions = defaultdict(set[pos.WordInfo])

for wi in pos.loadAncora('train'):
    if '_' in wi.word and '_' != wi.word:
        wi.word = wi.word.lower()
        locucions[wi.pos[0]].add(wi)

for pos_type, locs in locucions.items():
    print(pos_type, len(locs))
    with open(f'locucions/loc-{pos_type}.txt', 'w', encoding='utf-8') as f:
        for loc in sorted(locs, key=lambda loc: (loc.pos, loc.lemma, loc.word)):
            print(loc.pos, loc.lemma, loc.word, file=f)