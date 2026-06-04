import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import SystemInput, ProcessResponse

app = FastAPI(
    title="Metodo de Eliminación de Gauss-Jordan ",
    description="Backend de alta precisión para álgebra lineal computacional sin dependencias de alto nivel.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def estimate_matrix_inf_norm(matrix: list[list[float]]) -> float:
    # Calcula la norma infinito de una matriz (máxima suma absoluta de filas).
    return max(sum(abs(element) for element in row) for row in matrix)

@app.post("/api/v1/gauss-jordan", response_model=ProcessResponse)
async def solve_gauss_jordan(system: SystemInput):
    start_time = time.perf_counter()
    
    # Clonación profunda para evitar mutar el objeto original
    A = [row[:] for row in system.matrix_A]
    b = system.vector_b[:]
    n = len(A)
    
    # Construcción de una matriz identidad paralela para monitorizar y obtener A^-1 de forma exacta
    I = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    
    intermediate_steps = []
    total_flops_executed = 0
    
    # Guardar la norma infinito original de A
    norm_inf_A = estimate_matrix_inf_norm(A)
    
    # MOTOR ALGORÍTMICO DE GAUSS-JORDAN CON INVERSA SIMULTÁNEA
    for i in range(n):
        # Pivoteo Parcial Estricto
        max_row = i
        max_val = abs(A[i][i])
        
        for r in range(i + 1, n):
            current_abs = abs(A[r][i])
            if current_abs > max_val:
                max_val = current_abs
                max_row = r
        
        if max_row != i:
            A[i], A[max_row] = A[max_row], A[i]
            b[i], b[max_row] = b[max_row], b[i]
            I[i], I[max_row] = I[max_row], I[i]  # Reflejar pivoteo en la matriz inversa
        
        pivot = A[i][i]
        
        if abs(pivot) < 1e-15:
            raise HTTPException(
                status_code=400,
                detail=f"Error de Singularidad: Pivote destructivamente pequeño detectado "
                       f"en la diagonal ({i},{i}) con valor {pivot}. El sistema no tiene solución única."
            )
            
        # Normalización de la Fila Pivote (Se aplica a A, b e I)
        for j in range(i, n):
            A[i][j] /= pivot
            total_flops_executed += 1
        for j in range(n):
            I[i][j] /= pivot
            total_flops_executed += 1
        b[i] /= pivot
        total_flops_executed += 1

        # Eliminación Bidireccional Simultánea
        for r in range(n):
            if r != i:
                factor = A[r][i]
                
                if abs(factor) < 1e-15:
                    continue  # Escape contra el desperdicio de ciclos en ceros
                
                for j in range(i, n):
                    A[r][j] -= factor * A[i][j]
                    total_flops_executed += 1
                for j in range(n):
                    I[r][j] -= factor * I[i][j]
                    total_flops_executed += 1
                b[r] -= factor * b[i]
                total_flops_executed += 1
                
        # Capturar instantánea intermedia de la matriz aumentada (A | b)
        current_snapshot = [A[row][:] + [b[row]] for row in range(n)]
        intermediate_steps.append(current_snapshot)

    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000
    
    # Condición matemática real: ||A|| * ||A^-1||
    norm_inf_inv = estimate_matrix_inf_norm(I)
    condition_number = norm_inf_A * norm_inf_inv

    return ProcessResponse(
        solution=b,
        execution_time_ms=round(execution_time_ms, 4),
        flops_count=total_flops_executed,
        condition_number_est=round(condition_number, 2),
        intermediate_matrices=intermediate_steps
    )