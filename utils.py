from typing import Callable, Collection, TypeVar
from collections import defaultdict

WIKIPEDIA_CA_DOMAIN = 'https://ca.wikipedia.org'

T = TypeVar('T')
K = TypeVar('K')

def group(input:list[T], group_by:Callable[[T], K]) -> dict[K,list[T]]:
    ret = defaultdict(list)
    for item in input:
        ret[group_by(item)].append(item)
    return ret

def overlap(set1:set, set2:Collection):
    return not set1.isdisjoint(set2)