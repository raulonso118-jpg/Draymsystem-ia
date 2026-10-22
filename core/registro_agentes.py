# ==========================================================
# DRAYMSYSTEM IA
# REGISTRO DE AGENTES
# ==========================================================

from typing import Dict, List, Any


class RegistroAgentes:

    def __init__(self):

        self.agentes: Dict[str, Any] = {}

    # ======================================================
    # REGISTRAR
    # ======================================================

    def registrar(self, agente):

        tag = getattr(
            agente,
            "INTENT_TAG",
            None
        )

        if not tag:
            raise ValueError(
                "El agente no posee INTENT_TAG."
            )

        self.agentes[tag] = agente

    # ======================================================
    # ELIMINAR
    # ======================================================

    def eliminar(self, tag: str):

        if tag in self.agentes:
            del self.agentes[tag]

    # ======================================================
    # OBTENER
    # ======================================================

    def obtener(self, tag: str):

        return self.agentes.get(tag)

    # ======================================================
    # EXISTE
    # ======================================================

    def existe(self, tag: str) -> bool:

        return tag in self.agentes

    # ======================================================
    # LISTAR
    # ======================================================

    def listar(self):

        return list(
            self.agentes.values()
        )

    # ======================================================
    # OBTENER TODOS
    # ======================================================

    def obtener_todos(self):

        return self.agentes

    # ======================================================
    # BUSCAR CAPACES
    # ======================================================

    def buscar_capaces(self, tarea):

        candidatos = []

        for agente in self.agentes.values():

            try:

                if agente.puede_resolver(
                    tarea
                ):
                    candidatos.append(
                        agente
                    )

            except Exception:
                pass

        return candidatos

    # ======================================================
    # BUSCAR ESPECIALIDAD
    # ======================================================

    def buscar_por_especialidad(
        self,
        especialidad: str
    ):

        encontrados = []

        for agente in self.agentes.values():

            especialidades = getattr(
                agente,
                "SPECIALTIES",
                []
            )

            if especialidad in especialidades:

                encontrados.append(
                    agente
                )

        return encontrados

    # ======================================================
    # ESTADISTICAS
    # ======================================================

    def resumen(self):

        resultado = {}

        for tag, agente in self.agentes.items():

            resultado[tag] = {

                "nivel":
                getattr(
                    agente,
                    "AGENT_LEVEL",
                    1
                ),

                "rol":
                getattr(
                    agente,
                    "ROLE",
                    "autor"
                ),

                "especialidades":
                getattr(
                    agente,
                    "SPECIALTIES",
                    []
                )
            }

        return resultado

    # ======================================================
    # CANTIDAD
    # ======================================================

    def cantidad(self):

        return len(
            self.agentes
        )
