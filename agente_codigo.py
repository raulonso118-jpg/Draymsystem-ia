# ==========================================================
# DRAYMSYSTEM IA
# AGENTE DE CODIGO
# ==========================================================

from datetime import datetime

from agentes.agente_general import AgenteGeneral


class AgenteCodigo(AgenteGeneral):

    INTENT_TAG = "codigo"

    AGENT_LEVEL = 3

    ROLE = "desarrollador"

    SPECIALTIES = [
        "codigo",
        "programacion",
        "python",
        "javascript",
        "java",
        "csharp",
        "arquitectura",
        "api",
        "backend",
        "frontend",
        "debugging",
        "testing"
    ]

    PALABRAS_CLAVE = {
        "codigo",
        "programar",
        "funcion",
        "clase",
        "metodo",
        "python",
        "java",
        "javascript",
        "api",
        "backend",
        "frontend",
        "bug",
        "debug",
        "error",
        "algoritmo",
        "sql",
        "json",
        "yaml",
        "docker",
        "microservicio"
    }

    def __init__(self):

        super().__init__()

        self.fecha_creacion = (
            datetime.now()
        )

    # ======================================================
    # CAPACIDAD
    # ======================================================

    def puede_resolver(
        self,
        tarea
    ) -> bool:

        texto = str(
            tarea
        ).lower()

        for palabra in self.PALABRAS_CLAVE:

            if palabra in texto:
                return True

        return False

    # ======================================================
    # ANALIZAR TAREA
    # ======================================================

    def analizar_tarea(
        self,
        tarea
    ):

        texto = str(
            tarea
        ).lower()

        if "python" in texto:
            return "python"

        if "javascript" in texto:
            return "javascript"

        if "java" in texto:
            return "java"

        if "sql" in texto:
            return "sql"

        if "api" in texto:
            return "api"

        return "general"

    # ======================================================
    # GENERAR PROPUESTA
    # ======================================================

    def generar_propuesta(
        self,
        tarea,
        categoria
    ):

        return {
            "categoria": categoria,
            "objetivo": str(tarea),
            "acciones": [
                "analizar_requisitos",
                "diseñar_solucion",
                "implementar",
                "validar",
                "documentar"
            ]
        }

    # ======================================================
    # RESOLVER
    # ======================================================

    def resolver(
        self,
        tarea,
        contexto
    ):

        categoria = (
            self.analizar_tarea(
                tarea
            )
        )

        propuesta = (
            self.generar_propuesta(
                tarea,
                categoria
            )
        )

        return {

            "agente":
                self.INTENT_TAG,

            "categoria":
                categoria,

            "estado":
                "completada",

            "tarea":
                tarea,

            "propuesta":
                propuesta,

            "resultado":
                (
                    f"Tarea de programación "
                    f"analizada por "
                    f"{self.__class__.__name__}"
                ),

            "contexto":
                contexto
        }

    # ======================================================
    # REVISION BASICA
    # ======================================================

    def revisar_codigo(
        self,
        codigo: str
    ):

        observaciones = []

        if not codigo:

            observaciones.append(
                "Código vacío."
            )

            return observaciones

        if "TODO" in codigo:

            observaciones.append(
                "Contiene TODO pendientes."
            )

        if "print(" in codigo:

            observaciones.append(
                "Revisar impresiones de depuración."
            )

        if len(codigo) > 10000:

            observaciones.append(
                "Archivo muy grande."
            )

        return observaciones

    # ======================================================
    # ESTIMACION COMPLEJIDAD
    # ======================================================

    def estimar_complejidad(
        self,
        codigo: str
    ):

        if not codigo:
            return "baja"

        longitud = len(codigo)

        if longitud < 500:
            return "baja"

        if longitud < 2000:
            return "media"

        if longitud < 5000:
            return "alta"

        return "muy_alta"

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        datos = super().resumen()

        datos["tipo"] = (
            "desarrollo_software"
        )

        return datos


# Compatibilidad
AgenteProgramador = AgenteCodigo
