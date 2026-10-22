# ==========================================================
# DRAYMSYSTEM IA
# MOTOR DE ENJAMBRE
# ==========================================================

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional


class MotorEnjambre:
    """
    Coordina la ejecución de tareas entre varios agentes.

    No selecciona agentes ni planifica tareas.

    Responsabilidades:
    - Ejecutar una tarea con un agente.
    - Ejecutar varias asignaciones en paralelo.
    - Compartir contexto mediante el workspace.
    - Registrar resultados y errores.
    - Informar éxitos y fallos al selector.
    """

    def __init__(
        self,
        workspace,
        selector_agentes=None,
        max_trabajadores: int = 3
    ):

        self.workspace = workspace
        self.selector_agentes = selector_agentes
        self.max_trabajadores = max(
            1,
            int(max_trabajadores)
        )

    # ======================================================
    # DATOS DEL AGENTE
    # ======================================================

    @staticmethod
    def _obtener_tag(agente) -> str:

        return (
            getattr(agente, "INTENT_TAG", None)
            or getattr(agente, "TAG", None)
            or agente.__class__.__name__
        )

    # ======================================================
    # DATOS DE LA TAREA
    # ======================================================area(
        tarea,
        nombre: str,
        valor_default=None
    ):

        if isinstance(tarea, dict):
            return tarea.get(
                nombre,
                valor_default
            )

        return getattr(
            tarea,
            nombre,
            valor_default
        )

    @classmethod
    def _obtener_nombre_tarea(cls, tarea) -> str:

        nombre = cls._obtener_valor_tarea(
            tarea,
            "nombre"
        )

        if nombre:
            return str(nombre)

        if isinstance(tarea, str):
            return tarea

        return "tarea_sin_nombre"

    @classmethod
    def _obtener_descripcion_tarea(cls, tarea) -> str:

        descripcion = cls._obtener_valor_tarea(
            tarea,
            "descripcion"
        )

        if descripcion:
            return str(descripcion)

        if isinstance(tarea, str):
            return tarea

        return cls._obtener_nombre_tarea(
            tarea
        )

    # ======================================================
    # CONTEXTO COMPARTIDO
    # ======================================================

    def _crear_contexto(
        self,
        contexto_adicional: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        contexto = {
            "workspace": self.workspace.workspace,
            "resumen_workspace":
                self.workspace.obtener_resumen()
        }

        if contexto_adicional:
            contexto.update(
                contexto_adicional
            )

        return contexto

    # ======================================================
    # REGISTRAR EXITO O FALLO
    # ======================================================

    def _registrar_exito(
        self,
        tag_agente: str
    ):

        if self.selector_agentes is None:
            return

        try:
            self.selector_agentes.registrar_exito(
                tag_agente
            )
        except Exception:
            pass

    def _registrar_fallo(
        self,
        tag_agente: str
    ):

        if self.selector_agentes is None:
            return

        try:
            self.selector_agentes.registrar_fallo(
                tag_agente
            )
        except Exception:
            pass

    # ======================================================
    # EJECUTAR UNA ASIGNACION
    # ======================================================

    def ejecutar_asignacion(
        self,
        tarea,
        agente,
        contexto_adicional: Optional[
            Dict[str, Any]
        ] = None
    ) -> Dict[str, Any]:

        nombre_tarea = self._obtener_nombre_tarea(
            tarea
        )

        descripcion = (
            self._obtener_descripcion_tarea(
                tarea
            )
        )

        tag_agente = self._obtener_tag(
            agente
        )

        resultado_ejecucion = {
            "tarea": nombre_tarea,
            "agente": tag_agente,
            "estado": "fallida",
            "resultado": None,
            "error": None
        }

        try:

            contexto = self._crear_contexto(
                contexto_adicional
            )

            resultado = agente.ejecutar(
                descripcion,
                contexto
            )

            if resultado is None:
                raise ValueError(
                    "El agente devolvió un resultado vacío."
                )

            clave_resultado = (
                f"resultado_{nombre_tarea}"
            )

            self.workspace.guardar(
                clave_resultado,
                {
                    "agente": tag_agente,
                    "contenido": resultado
                }
            )

            resultado_ejecucion[
                "estado"
            ] = "completada"

            resultado_ejecucion[
                "resultado"
            ] = resultado

            self._registrar_exito(
                tag_agente
            )

        except Exception as error:

            mensaje_error = str(error)

            resultado_ejecucion[
                "error"
            ] = mensaje_error

            self.workspace.guardar(
                f"error_{nombre_tarea}",
                {
                    "agente": tag_agente,
                    "error": mensaje_error
                }
            )

            self._registrar_fallo(
                tag_agente
            )

        return resultado_ejecucion

    # ======================================================
    # EJECUTAR VARIAS ASIGNACIONES
    # ======================================================

    def ejecutar(
        self,
        asignaciones: List[Dict[str, Any]],
        contexto_adicional: Optional[
            Dict[str, Any]
        ] = None
    ) -> List[Dict[str, Any]]:

        if not asignaciones:
            return []

        resultados = []

        cantidad_trabajadores = min(
            self.max_trabajadores,
            len(asignaciones)
        )

        with ThreadPoolExecutor(
            max_workers=cantidad_trabajadores
        ) as ejecutor:

            futuros = {}

            for asignacion in asignaciones:

                tarea = asignacion.get(
                    "tarea"
                )

                agente = asignacion.get(
                    "agente"
                )

                if tarea is None or agente is None:

                    resultados.append(
                        {
                            "tarea": (
                                self._obtener_nombre_tarea(
                                    tarea
                                )
                            ),
                            "agente": None,
                            "estado": "fallida",
                            "resultado": None,
                            "error": (
                                "La asignación necesita "
                                "una tarea y un agente."
                            )
                        }
                    )

                    continue

                futuro = ejecutor.submit(
                    self.ejecutar_asignacion,
                    tarea,
                    agente,
                    contexto_adicional
                )

                futuros[futuro] = (
                    self._obtener_nombre_tarea(
                        tarea
                    )
                )

            for futuro in as_completed(
                futuros
            ):

                nombre_tarea = futuros[
                    futuro
                ]

                try:

                    resultado = futuro.result()

                except Exception as error:

                    resultado = {
                        "tarea": nombre_tarea,
                        "agente": None,
                        "estado": "fallida",
                        "resultado": None,
                        "error": str(error)
                    }

                resultados.append(
                    resultado
                )

        resultados.sort(
            key=lambda elemento: elemento[
                "tarea"
            ]
        )

        self.workspace.guardar(
            "ultima_ejecucion_enjambre",
            resultados
        )

        try:
            self.workspace.guardar_disco()
        except Exception:
            pass

        return resultados

    # ======================================================
    # RESUMEN DE EJECUCION
    # ======================================================

    @staticmethod
    def resumir_resultados(
        resultados: List[Dict[str, Any]]
    ) -> Dict[str, int]:

        completadas = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == "completada"
        )

        fallidas = sum(
            1
            for resultado in resultados
            if resultado.get("estado")
            == "fallida"
        )

        return {
            "total": len(resultados),
            "completadas": completadas,
            "fallidas": fallidas
        }


# Compatibilidad con un nombre más corto
Enjambre = MotorEnjambre
