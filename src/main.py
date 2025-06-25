from model import PosModel


if __name__ == '__main__':
    model = PosModel('ancora', pos_len=2)
    with open('data/minitrain/wiki.txt', encoding='utf-8') as in_:
        with open('data/minitrain/wiki.pos.txt', 'w', encoding='utf-8') as out:
            for line in in_.readlines():
                tokens = model.tokenize(line)
                pos_vecs = model.predictPos(tokens)
                for (t, options), p in zip(tokens, pos_vecs):
                    options = set(wi.pos[:2] for wi in options)
                    print(p, t, '\t', ','.join(options) if len(set(options)) > 1 else '', file=out)
                print(file=out)
                out.flush()