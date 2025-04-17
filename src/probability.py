import numpy as np

def oneHot(size:int, index:int):
    """Create a one-hot encoded vector of size `size` with a 1 at `index`."""
    assert 0 <= index < size, f'Index {index} out of bounds for size {size}'
    ret = np.zeros(size, dtype=np.float32)
    ret[index] = 1.0
    return ret

def distribution(matrix:np.ndarray):
    return matrix/sum(matrix)

def combination(old, new, / , labels=None):
    mult = old*new
    comp_mult = (1-old)*(1-new)
    #combination = mult/prob_a_priori
    combination = mult/(mult + comp_mult)
    probabilities = distribution(combination**0.8)
    if labels is not None:
        for pos,p1,p2,p3 in zip(labels, old, new, combination):
            if p1>0 or p3>0:
                print(f'{pos}:{p1:.4f}++{p2:.4f}={p3:.4f}', end=', ')
        print(' -> ', end='')
        for pos,p in zip(labels, probabilities):
            if p>0:
                print(f'{pos}:{p:.4f}', end=', ')
        print()
    return probabilities

def uniform(size:int):
    return np.ones(size)/size
