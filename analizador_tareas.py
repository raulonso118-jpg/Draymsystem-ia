# ==========================================================
# DRAYMSYSTEM IA
# ANALIZADOR DE TAREAS
# ==========================================================

class AnalizadorTareas:

    def __init__(self):

        self.categorias = {

            "codigo": [
                "python",
                "programa",
                "codigo",
                "funcion",
                "script",
                "api",
                "algoritmo"
            ],

            "arquitectura": [
                "arquitectura",
                "sistema",
                "estructura",
                "modulo",
                "diseño"
            ],

            "libro": [
                "libro",
                "capitulo",
                "novela",
                "historia",
                "personaje"
            ],

            "investigacion": [
                "investigar",
                "analizar",
                "buscar",
                "estudiar"
            ],

            "qa": [
                "error",
                "fallo",
                "bug",
                "corregir",
                "validar"
            ]
        }

    # ======================================================
    # CLASIFICAR
    # ======================================================

    def clasificar(self, tarea):

        texto = tarea.lower()

        puntuaciones = {}

        for categoria, palabras in self.categorias.items():

            puntuacion = 0

            for palabra in palabras:

                if palabra in texto:
                    puntuacion += 1

            puntuaciones[categoria] = puntuacion

        mejor_categoria = max(
            puntuaciones,
            key=puntuaciones.get
        )

        if puntuaciones[mejor_categoria] == 0:
            return "general"

        return mejor_categoria

    # ======================================================
    # ANALIZAR
    # ======================================================

    def analizar(self, tarea):

        return {
            "categoria":
            self.clasificar(tarea),

            "texto":
            tarea
        }
