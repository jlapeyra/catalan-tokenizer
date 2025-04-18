from abc import abstractmethod
from collections import Counter, defaultdict
from typing import Callable, TypeVar
import numpy as np

_K1T = TypeVar("_KT")
_K2T = TypeVar("_KT")
_VT = TypeVar("_VT")

class DoubleKeyCounter(Counter):
    _keys1 = None
    _keys2 = None

    def _get(self, k1, k2):
        return self[k1, k2]
    
    def _set(self, k1, k2, value):
        self[k1, k2] = value
    
    def _compute_keys(self, i):
        return sorted({k[i] for k in self.keys()})

    def __get_keys(self, i) -> list:
        if self._keys is None:
            print('computing keys for', self.__class__.__name__)
            self._keys = self._compute_keys(0), self._compute_keys(1)
        return self._keys[i]
    
    def set_keys(self, keys1:list, keys2:list):
        self._keys = keys1, keys2

    def keys1(self) -> list:
        '''Returns a set of all first-level keys in the counter.'''
        return self.__get_keys(0)

    def keys2(self) -> list:
        '''Returns a set of all second-level keys in the counter.'''
        return self.__get_keys(1)

    def __setitem__(self, key, value):
        assert len(key) == 2
        return super().__setitem__(key, value)

    def matrix(self, dtype=np.int64) -> np.ndarray:
        '''
            Generates a 2D NumPy array (matrix) where rows correspond to sorted first-level keys (k1),
            columns correspond to sorted second-level keys (k2), and the values are retrieved using 
            the get(k1, k2) method. Returns the matrix along with the sorted lists of keys1 and keys2.
        '''
        keys1 = self.keys1()
        keys2 = self.keys2()
        matrix = np.zeros((len(keys1), len(keys2)), dtype=dtype)
        for i1, k1 in enumerate(keys1):
            for i2, k2 in enumerate(keys2):
                matrix[i1, i2] = self._get(k1, k2)
        return matrix
    

class HDoubleKeyCounter(defaultdict[_K1T, dict[_K2T, _VT]], DoubleKeyCounter):
    '''
    A hierarchical counter that supports two levels of keys. This class extends
    `defaultdict` to provide a convenient way to manage nested dictionaries and 
    implements additional methods for accessing and manipulating the data.

    Inherits:
        - `defaultdict[_K1T, dict[_K2T, _VT]]`: A defaultdict where the default factory 
        produces dictionaries.
        - `DoubleKeyCounter`: A custom base class that provides methods for 
        handling dictionaries with two levels of keys.
    '''
    def __init__(self, default_factory: Callable[[], dict[_K2T, _VT]] = Counter):
        '''
        The `default_factory` must produce dictionaries to ensure proper functionality.
        '''
        return super().__init__(default_factory)

    def _get(self, k1, k2):
        return self[k1][k2]
    
    def _set(self, k1, k2, value):
        self[k1][k2] = value

    def _compute_keys(self, i):
        if i == 0:
            return sorted(self.keys())
        elif i == 1:
            return sorted(set().union(*(dist.keys() for dist in self.values())))
    
    def __setitem__(self, key, value):
        assert isinstance(value, dict)
        return super().__setitem__(key, value)
    
class Symmetric2KeyCounter(DoubleKeyCounter):
    '''
    A counter-like class that enforces symmetry in its keys. This means that 
    the order of the keys in a tuple does not matter, and the keys are always 
    stored in sorted order. For example, accessing or setting the value for 
    the key ('a', 'b') is equivalent to accessing or setting the value for 
    the key ('b', 'a').
    Inherits:
        - `DoubleKeyCounter`: A custom base class that provides methods for 
        handling dictionaries with two levels of keys.
    '''
    __keys = None

    def _compute_keys(self, i):
        if self.__keys is None:
            return sorted(set(super()._compute_keys(0) +  super()._compute_keys(1)))

    def __getitem__(self, key):
        return super().__getitem__(tuple(sorted(key)))
    def __setitem__(self, key, value):
        return super().__setitem__(tuple(sorted(key)), value)
    

if __name__ == '__main__':
    for klass in Pair2KeyCounter, Hier2KeyCounter, Symmetric2KeyCounter:
        dkd = klass()
        dkd.set(2,1, 4)
        dkd.set(6,5, 7)
        print(dkd.matrix())
        print(dkd.keys1())
        print(dkd.keys2())
