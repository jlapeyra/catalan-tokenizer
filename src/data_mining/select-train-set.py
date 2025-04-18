from glob import glob

out = open('data/minitrain.md', 'w', encoding='utf-8')

print('# EUROPARL', file=out)
with open('data/minitrain/europarl.txt', 'w', encoding='utf-8') as data:
    with open('data-raw/europarl/europarl-v7.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        end = len(lines)//20
        data.write(''.join(lines[:end]))
        print('lines', f'{0}-{end}', file=out)
print(file=out)

print('# WIKI', file=out)
with open('data/minitrain/wiki.txt', 'w', encoding='utf-8') as data:
    for fn in glob('data-raw/wiki/*.txt')[::5]:
        print(fn, file=out)
        with open(fn, 'r', encoding='utf-8') as f:
            data.write(f.read())
print(file=out)

print('# PODCAST', file=out)
with open('data/minitrain/podcast.txt', 'w', encoding='utf-8') as data:
    for fn in glob('data-raw/softcatala-podcast-corpus/*/*.txt')[::2]:
        print(fn, file=out)
        with open(fn, 'rb') as f:
            text = f.read().decode('utf-8', errors='ignore')
            data.write(text)
print(file=out)



with open(__file__, 'r', encoding='utf-8') as f:
    out.write('\n\n```\n' + f.read() + '\n```\n')


out.close()

