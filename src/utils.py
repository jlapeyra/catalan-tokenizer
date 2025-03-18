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

def splitList(l:list, sep=None, seps=None, sep_func=None, not_empty=False, keep_sep=True) -> list:
    assert (sep is not None) + (seps is not None) + (sep_func is not None) == 1
    if not sep_func:
        if sep!=None: sep_func = lambda x: x == sep
        else:         sep_func = lambda x: x in seps
    def append(sublist:list):
        if not not_empty or sublist:
            retorn.append(sublist)
    retorn = []
    start = 0
    for i, elem in enumerate(l):
        if sep_func(elem):
            end = i+1 if keep_sep else i
            append(l[start:end])
            start = i+1
    append(l[start:])
    return retorn

    