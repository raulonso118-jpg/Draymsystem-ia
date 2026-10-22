# ==========================================================
# DRAYMSYSTEM IA
# AGENTE GENERAL
# ==========================================================

from datetime import datetime

from agentes.base_agente import BaseAgente


class AgenteGeneral(BaseAgente):

    """
    Agente multipropósito.

    Es el agente por defecto cuando ninguna
    especialidad específica aplica.

    También sirve como clase base para agentes
    especializados.
    """

    INTENT_TAG = "general"

    AGENT_LEVEL = 1

    ROLE = "generalista"

    SPECIALTIES = [
        "general",
        "texto",
        "consulta",
        "analisis"
    ]

    def __init__(self):

        super().__init__()

        self.total_tareas = 0

        self.total_exitos = 0

        self.total_fallos = 0

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

        return True

    # ======================================================
    # PREPARAR
    # ======================================================

    def preparar_contexto(
        self,
        tarea,
        contexto=None
    ):

        return {
            "tarea": tarea,
            "contexto": contexto or {},
            "timestamp":
                datetime.now().isoformat()
        }

    # ======================================================
    # EJECUTAR
    # ======================================================

    def ejecutar(
        self,
        tarea,
        contexto=None
    ):

        self.total_tareas += 1

        try:

            contexto_preparado = (
                self.preparar_contexto(
                    tarea,
                    contexto
                )
            )

            resultado = (
                self.resolver(
                    tarea,
                    contexto_preparado
                )
            )

            self.total_exitos += 1

            return resultado

        except Exception as error:

            self.total_fallos += 1

            raise error

    # ======================================================
    # RESOLVER
    # ======================================================

    def resolver(
        self,
        tarea,
        contexto
    ):

        return {

            "agente":
                self.INTENT_TAG,

            "tarea":
                tarea,

            "estado":
                "completada",

            "resultado":
                (
                    f"Tarea recibida y "
                    f"procesada por "
                    f"{self.__class__.__name__}"
                ),

            "contexto":
                contexto
        }

    # ======================================================
    # EXPERIENCIA
    # ======================================================

    def registrar_exito(self):

        self.total_exitos += 1

    def registrar_fallo(self):

        self.total_fallos += 1

    # ======================================================
    # METRICAS
    # ======================================================

    def tasa_exito(self):

        if self.total_tareas == 0:
            return 0.0

        return (
            self.total_exitos
            /
            self.total_tareas
        )

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        return {

            "agente":
                self.INTENT_TAG,

            "nivel":
                self.AGENT_LEVEL,

            "rol":
                self.ROLE,

            "especialidades":
                self.SPECIALTIES,

            "tareas":
                self.total_tareas,

            "exitos":
                self.total_exitos,

            "fallos":
                self.total_fallos,

            "tasa_exito":
                round(
                    self.tasa_exito(),
                    4
                )
        }

    # ======================================================
    # REPRESENTACION
    # ======================================================

    def __str__(self):

        return (
            f"{self.__class__.__name__}"
            f"(tag={self.INTENT_TAG})"
        )

    def __repr__(self):

        return self.__str__()
