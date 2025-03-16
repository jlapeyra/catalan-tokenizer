import sys
import pos

if __name__ == '__main__':
    dataset = sys.argv[1]
    with open(f'corpus/{dataset}.pos.txt', 'w', encoding='utf-8') as out:
        with open(f'corpus/{dataset}.txt', 'r', encoding='utf-8') as in_:
            count = 0
            for paragraf in in_:
                pos.printAssignacio(pos.assignarCategories(paragraf), out)
                count += 1
                #if count > 20:
                #    break
                #print('\n\n\n', end='', file=out) #indica canvi de paràgraf
