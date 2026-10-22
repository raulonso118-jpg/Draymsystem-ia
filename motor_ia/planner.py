# ==========================================================
# DRAYMSYSTEM IA
# PLANNER DE OBJETIVOS
# ==========================================================

class Planner:

    def __init__(self):

        self.plantillas = {

            "arquitectura": [

                "Analizar requerimientos",

                "Diseñar arquitectura",

                "Definir módulos",

                "Validar estructura"
            ],

            "codigo": [

                "Analizar problema",

                "Diseñar solución",

                "Implementar código",

                "Realizar pruebas"
            ],

            "libro": [

                "Investigar tema",

                "Crear estructura",

                "Redactar contenido",

                "Revisar y corregir"
            ],

            "investigacion": [

                "Recopilar información",

                "Analizar datos",

                "Extraer conclusiones"
            ],

            "qa": [

                "Identificar errores",

                "Analizar causa",

                "Validar corrección"
            ]
        }

    # ======================================================
    # CREAR PLAN
    # ======================================================

    def crear_plan(
        self,
        categoria
    ):

        return self.plantillas.get(

            categoria,

            [

                "Analizar solicitud",

                "Ejecutar tarea",

                "Validar resultado"

            ]
        )
