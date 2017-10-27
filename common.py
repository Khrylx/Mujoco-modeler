import numpy as np


def norm(v):
    return np.linalg.norm(v)


def normalize(v):
    return v / norm(v)
