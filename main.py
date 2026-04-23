from fastapi import FastAPI
import math

app = FastAPI()

R = 3   # radio del tanque
V = 30  # volumen deseado

# Función del tanque
def f(h):
    return (math.pi * h**2 * (3*R - h)) / 3 - V

# Derivada (para Newton)
def df(h):
    return math.pi * h * (2*R - h)

@app.post("/newton")
def newton(data: dict):
    h = data["h_inicial"]
    tolerancia = data["tolerancia"]
    max_iter = data["max_iter"]

    iteraciones = []

    for i in range(max_iter):
        if df(h) == 0:
            return {"error": "Derivada cero"}

        h_nuevo = h - f(h)/df(h)
        error = abs(h_nuevo - h)

        iteraciones.append({
            "iteracion": i,
            "h": h,
            "f(h)": f(h),
            "error": error
        })

        if error < tolerancia:
            return {
                "metodo": "Newton-Raphson",
                "iteraciones": iteraciones,
                "resultado_final": h_nuevo,
                "mensaje": "Altura óptima del agua en el tanque"
            }

        h = h_nuevo

    return {"mensaje": "No convergió"}


@app.post("/secante")
def secante(data: dict):
    h0 = data["h0"]
    h1 = data["h1"]
    tolerancia = data["tolerancia"]
    max_iter = data["max_iter"]

    iteraciones = []

    for i in range(max_iter):
        if (f(h1) - f(h0)) == 0:
            return {"error": "División por cero"}

        h2 = h1 - f(h1)*(h1 - h0)/(f(h1) - f(h0))
        error = abs(h2 - h1)

        iteraciones.append({
            "iteracion": i,
            "h": h1,
            "f(h)": f(h1),
            "error": error
        })

        if error < tolerancia:
            return {
                "metodo": "Secante",
                "iteraciones": iteraciones,
                "resultado_final": h2,
                "mensaje": "Altura óptima del agua en el tanque"
            }

        h0 = h1
        h1 = h2

    return {"mensaje": "No convergió"}

@app.get("/")
def inicio():
    return {"mensaje": "API de métodos numéricos aplicada a la agricultura"}
