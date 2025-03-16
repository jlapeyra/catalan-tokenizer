from glob import glob
import distribution
import utils
import pos
import re





def from_annotated_corpus():

    # 2-gram of POS
    # probability of POS given previous/next POS

    n = 2
    ngram = distribution.NGram(n, ['-'])
    for filename in glob('corpus/train.pos.txt'):
        #dataset = sys.argv[1]
        with open(filename, 'r', encoding='utf-8') as f:
            assignacio = pos.readAssignacio(f)
        pos_list_full = [pos for _, pos in assignacio]
        for pos_list in utils.splitList(pos_list_full, seps=('.', '$'), not_empty=True):
            ngram.feed(pos_list)
    with open(f'model/pos.{n}gram.txt', 'w') as f:
        ngram.save(f)


    # probability of POS given word

    probs = distribution.ConditionalDistribution()
    for fn in glob('corpus/train.pos.txt'):
        with open(fn, 'r', encoding='utf-8') as f:
            assignacio = pos.readAssignacio(f)
        for i, (paraula, pos_) in enumerate(assignacio):
            if not re.match(pos.RE_PUNCTUATION+'$', paraula.lower()):
                pos_pos = pos.categoriesPossibles(paraula)
                if pos_pos and pos_ not in pos_pos:
                    print(f'WARNING: {paraula} {pos_} {pos_pos}', \
                          '\t'+' '.join(w for w,p in assignacio[i-5:i+5]))
                probs.add(paraula.lower(), pos_)
    for key in list(probs.keys()):
        if probs[key].total() < 8:
            del probs[key]
    with open('model/pos.count.txt', 'w', encoding='utf-8') as f:
        probs.save(f)



if __name__ == '__main__':
    from_annotated_corpus()