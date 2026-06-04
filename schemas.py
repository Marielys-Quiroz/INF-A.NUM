from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List

class SystemInput(BaseModel):
    matrix_A: List[List[float]]
    vector_b: List[float]

    @field_validator('matrix_A')
    @classmethod
    def check_dimensions(cls, v: List[List[float]]) -> List[List[float]]:
        n = len(v)
        if n == 0:
            raise ValueError("La matriz de coeficientes A no puede estar vacía.")
        for row_idx, row in enumerate(v):
            if len(row) != n:
                raise ValueError(f"La fila {row_idx} tiene longitud {len(row)}. A debe ser cuadrada (n x n).")
        return v

    @field_validator('vector_b')
    @classmethod
    def check_vector_length(cls, v: List[float], info: ValidationInfo) -> List[float]:
        matrix_A = info.data.get('matrix_A')
        if matrix_A is not None and len(v) != len(matrix_A):
            raise ValueError(
                f"Consistencia rota: El vector b tiene dimensión {len(v)}, "
                f"pero la matriz A es de tamaño {len(matrix_A)}x{len(matrix_A)}."
            )
        return v

class ProcessResponse(BaseModel):
    solution: List[float]
    execution_time_ms: float
    flops_count: int
    condition_number_est: float
    intermediate_matrices: List[List[List[float]]]