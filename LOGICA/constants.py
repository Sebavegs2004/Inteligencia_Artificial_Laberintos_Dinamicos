from enum import IntEnum

class CellType(IntEnum):
    CAMINO = 0
    MURO = 1
    SALIDA = 2
    SALIDA_FALSA = 3