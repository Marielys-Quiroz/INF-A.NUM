import reflex as rx
import requests
from typing import List, Dict

# --- CONFIGURACIÓN ---
API_NEWTON = "http://127.0.0.1:8000/newton_tanque"
API_SECANTE = "http://127.0.0.1:8000/secante_poly"
URL_FONDO = "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?q=80&w=2070&auto=format&fit=crop"

class State(rx.State):
    """Estado con setters manuales para evitar errores de compilación"""
    h_inicial: str = ""
    x0: str = ""
    x1: str = ""
    tolerancia: str = ""
    max_iter: str = ""
    
    iteraciones: List[Dict] = []
    resultado_raiz: str = "---"
    grafico_puntos: List[Dict] = []

    # SETTERS EXPLÍCITOS PARA EVITAR ATTRIBUTEERROR
    def set_h_inicial(self, v: str): self.h_inicial = v
    def set_x0(self, v: str): self.x0 = v
    def set_x1(self, v: str): self.x1 = v
    def set_tolerancia(self, v: str): self.tolerancia = v
    def set_max_iter(self, v: str): self.max_iter = v

    def calcular_newton(self):
        try:
            res = requests.post(API_NEWTON, json={
                "h_inicial": float(self.h_inicial) if self.h_inicial else 0,
                "tolerancia": float(self.tolerancia) if self.tolerancia else 0.0001,
                "max_iter": int(self.max_iter) if self.max_iter else 10
            }).json()
            self.iteraciones = res.get("iteraciones", [])
            if self.iteraciones:
                self.resultado_raiz = str(self.iteraciones[-1]["x"])
                self.grafico_puntos = [{"n": str(i["n"]), "valor": float(i["x"])} for i in self.iteraciones]
        except:
            self.resultado_raiz = "Error: Backend no responde"

    def calcular_secante(self):
        try:
            res = requests.post(API_SECANTE, json={
                "x0": float(self.x0) if self.x0 else 0,
                "x1": float(self.x1) if self.x1 else 0,
                "tolerancia": float(self.tolerancia) if self.tolerancia else 0.0001,
                "max_iter": int(self.max_iter) if self.max_iter else 10
            }).json()
            self.iteraciones = res.get("iteraciones", [])
            if self.iteraciones:
                self.resultado_raiz = str(self.iteraciones[-1]["x_next"])
                self.grafico_puntos = [{"n": str(i["n"]), "valor": float(i["x_next"])} for i in self.iteraciones]
        except:
            self.resultado_raiz = "Error: Backend no responde"

def index():
    return rx.center(
        rx.vstack(
            rx.heading("🚜 Análisis Numérico Agrícola 🌾", size="8", color="white", text_shadow="2px 2px 4px black"),
            
            rx.box(
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("📍 TANGENTE", value="t1", color="black"),
                        rx.tabs.trigger("🔗 SECANTE", value="t2", color="black"),
                    ),
                    # --- PANEL TANGENTE (NEWTON) ---
                    rx.tabs.content(
                        rx.vstack(
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Altura h", color="black", weight="bold"),
                                    rx.input(placeholder="Ej: 2.0", value=State.h_inicial, on_change=State.set_h_inicial, color="black", border_color="gray"),
                                    rx.text("Tolerancia", color="black", weight="bold"),
                                    rx.input(placeholder="0.0001", value=State.tolerancia, on_change=State.set_tolerancia, color="black", border_color="gray"),
                                    rx.text("Max Iter", color="black", weight="bold"),
                                    rx.input(placeholder="10", value=State.max_iter, on_change=State.set_max_iter, color="black", border_color="gray"),
                                    rx.button("🚀 CALCULAR", on_click=State.calcular_newton, width="100%", bg="black", color="white"),
                                    width="30%", spacing="3"
                                ),
                                rx.vstack(
                                    rx.text("📊 Gráfica de Convergencia", color="black", weight="bold"),
                                    rx.recharts.line_chart(
                                        rx.recharts.line(data_key="valor", stroke="#22c55e", stroke_width=2),
                                        rx.recharts.x_axis(data_key="n", stroke="black"),
                                        rx.recharts.y_axis(domain=['auto', 'auto'], stroke="black"),
                                        data=State.grafico_puntos, width=550, height=250
                                    ), width="70%"
                                ), width="100%"
                            ),
                            rx.divider(border_color="black"),
                            rx.text(f"🚩 RESULTADO: {State.resultado_raiz}", size="6", weight="bold", color="black"),
                            rx.scroll_area(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("n", color="black"),
                                            rx.table.column_header_cell("X", color="black"),
                                            rx.table.column_header_cell("F(x)", color="black"),
                                            rx.table.column_header_cell("F'(x)", color="black"),
                                            rx.table.column_header_cell("Converge", color="black")
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(State.iteraciones, lambda i: rx.table.row(
                                            rx.table.cell(i["n"], color="black"),
                                            rx.table.cell(i["x"], color="black"),
                                            rx.table.cell(i["fx"], color="black"),
                                            rx.table.cell(i["dfx"], color="black"),
                                            rx.table.cell(i["error_res"], color="black")
                                        ))
                                    ), variant="surface", width="100%"
                                ), height="250px"
                            )
                        ), value="t1", padding="1.5em"
                    ),
                    # --- PANEL SECANTE ---
                    rx.tabs.content(
                        rx.vstack(
                            rx.hstack(
                                rx.vstack(
                                    rx.text("Punto x0", color="black", weight="bold"),
                                    rx.input(value=State.x0, on_change=State.set_x0, color="black", border_color="gray"),
                                    rx.text("Punto x1", color="black", weight="bold"),
                                    rx.input(value=State.x1, on_change=State.set_x1, color="black", border_color="gray"),
                                    rx.text("Tolerancia", color="black", weight="bold"),
                                    rx.input(value=State.tolerancia, on_change=State.set_tolerancia, color="black", border_color="gray"),
                                    rx.button("🚀 CALCULAR", on_click=State.calcular_secante, width="100%", bg="blue", color="white"),
                                    width="30%", spacing="3"
                                ),
                                rx.vstack(
                                    rx.text("📊 Evolución Polinomial", color="black", weight="bold"),
                                    rx.recharts.line_chart(
                                        rx.recharts.line(data_key="valor", stroke="#3b82f6", stroke_width=2),
                                        rx.recharts.x_axis(data_key="n", stroke="black"),
                                        rx.recharts.y_axis(domain=['auto', 'auto'], stroke="black"),
                                        data=State.grafico_puntos, width=550, height=250
                                    ), width="70%"
                                ), width="100%"
                            ),
                            rx.divider(border_color="black"),
                            rx.text(f"🚩 RESULTADO: {State.resultado_raiz}", size="6", weight="bold", color="black"),
                            rx.scroll_area(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("n", color="black"),
                                            rx.table.column_header_cell("Xi-1", color="black"),
                                            rx.table.column_header_cell("Xi", color="black"),
                                            rx.table.column_header_cell("F(Xi)", color="black"),
                                            rx.table.column_header_cell("Xi+1", color="black"),
                                            rx.table.column_header_cell("Error %", color="black")
                                        )
                                    ),
                                    rx.table.body(
                                        rx.foreach(State.iteraciones, lambda i: rx.table.row(
                                            rx.table.cell(i["n"], color="black"),
                                            rx.table.cell(i["xi_1"], color="black"),
                                            rx.table.cell(i["xi"], color="black"),
                                            rx.table.cell(i["f_xi"], color="black"),
                                            rx.table.cell(i["x_next"], color="black"),
                                            rx.table.cell(i["error_pct"], color="black")
                                        ))
                                    ), variant="surface", width="100%"
                                ), height="250px"
                            )
                        ), value="t2", padding="1.5em"
                    ),
                ),
                bg="rgba(255, 255, 255, 0.95)", 
                border_radius="15px", 
                border="2px solid black", 
                width="100%"
            ),
        ),
        style={
            "background_image": f"url('{URL_FONDO}')",
            "background_size": "cover",
            "background_attachment": "fixed",
            "min_height": "100vh",
            "padding": "2em"
        }
    )

app = rx.App()
app.add_page(index)