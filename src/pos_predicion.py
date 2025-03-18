import numpy as np
import probability
from collections import defaultdict
from typing import Iterable
from diccionari import getDiccionari
from utils import group
import pos
from pos_model import PosModel


exemple = 'Jo la vaig veure un dia clar, sota una llum que m\'encegava i quan la vaig gosar mirar ella em tornava la mirada.' \
    #'I ara en les nits que em gronxo al mar, quan vaig mirant la lluna clara, ja no sé veure més que un far des d\'on somriu la seva cara'
#exemple = 'I avui també.'

test_data = open('corpus/espanya.wiki.txt', encoding='utf-8').read()

m = PosModel()


words = pos.splitWords(test_data)


with open('corpus/espanya.wiki.pos.txt', 'w', encoding='utf-8') as f:
    pos.printAssignacio(zip(words, map(posMax, pos_vecs)), f)

print_pos(words, pos_vecs, limit=100)

pass