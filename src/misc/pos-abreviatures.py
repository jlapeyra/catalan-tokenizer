import re

abr1 = []
abr2 = []

with open('diccionari/pos-exemples.txt', encoding='utf-8') as f:
    for line in f:
        if re.match(r'\t?[A-Z]', line):
            if line[0] != '\t':
                abr1.append(line.strip())
            else:
                abr2.append(line.strip())


with open('diccionari/pos-abreviatures.txt', 'w', encoding='utf-8') as f:
    for line in abr1:
        f.write(line + '\n')
    f.write('\n')
    for line in abr2:
        f.write(line + '\n')
