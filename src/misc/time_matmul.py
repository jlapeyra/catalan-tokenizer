from others.elapsed_time import elapsed_time
import random
import numpy as np

def dotmul(matrix:np.ndarray, array:np.ndarray):
    return np.array([
        np.dot(array, matrix[i])
        for i in range(matrix.shape[0])
    ])
    


t_dot = 0
t_at = 0
t_matmul = 0

np.random.seed(3)

print('at\tmul\tdot')

for i in range(100):
    n = 7_000 + 120*i
    matrix = np.random.randint(0,2**20, (n,n))
    array  = np.random.randint(0,2**20, n)
    t1, r1 = elapsed_time(lambda: array @ matrix, True)
    t2, r2 = elapsed_time(lambda: np.matmul(array, matrix), True)
    t3, r3 = elapsed_time(lambda: dotmul(matrix, array), True)
    t_at += t1
    t_matmul += t2
    t_dot += t3
    assert np.allclose(r1, r2)
    assert np.allclose(r1, r3)
    print('\r', end='')
    print(t_at, t_matmul, t_dot, f'      n={n}, n*n={n*n}, ({i+1}/100)', end=' '*20)


