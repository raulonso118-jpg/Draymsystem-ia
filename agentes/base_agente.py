# ==========================================================
# DRAYMSYSTEM IA
# PROTOCOLO BASE DE AGENTES
# ==========================================================

from abc import ABC
from abc import abstractmethod


class BaseAgente(ABC):

    # ------------------------------------------------------
    # IDENTIDAD
    # ------------------------------------------------------

    NOMBRE = "AgenteBase"

    TAG = "general"

    DESCRIPCION = "Agente genérico"

    PRIORIDAD = 1

    # ------------------------------------------------------
    # CONSTRUCTOR
    # ------------------------------------------------------

    def __init__(self):

        self.activo = True

    # ------------------------------------------------------
    # CAPACIDADES
    # ------------------------------------------------------

    @abstractmethod
    def puede_resolver(
        self,
        tarea
    ):
        pass

    # ------------------------------------------------------
    # EJECUCIÓN
    # ------------------------------------------------------

    @abstractmethod
    def ejecutar(
        self,
        tarea,
        contexto
    ):
        pass

    # ------------------------------------------------------
    # INFORMACIÓN
    # ------------------------------------------------------

    def obtener_info(self):

        return {
            "nombre": self.NOMBRE,
            "tag": self.TAG,
            "descripcion": self.DESCRIPCION,
            "prioridad": self.PRIORIDAD
        }
