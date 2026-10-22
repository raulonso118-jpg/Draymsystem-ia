# ==========================================================
# DRAYMSYSTEM IA
# INTEGRADOR DE RESULTADOS
# ==========================================================

from datetime import datetime
from typing import Any, Dict, List, Optional


class Integrador:
    """
    Une los resultados aprobados del enjambre en una sola salida.

    Responsabilidades:
    - Verificar el dictamen del supervisor.
    - Excluir resultados fallidos o rechazados.
    - Evitar integrar contenido duplicado.
    - Ordenar los resultados según las tareas esperadas.
    - Construir una salida final coherente.
    - Guardar la integración en el workspace.

    El integrador no ejecuta agentes, no supervisa y no corrige
    contenidos. Solo organiza los resultados ya aprobados.
    """

    def __init__(
        self,
        permitir_integracion_parcial: bool = False
    ):

        self.permitir_integracion_parcial = bool(
            permitir_integracion_parcial
        )

    # ======================================================
    # NORMALIZAR TEXTO
    # ======================================================

    @staticmethod
    def _normalizar_texto(
        contenido: Any
    ) -> str:

        if contenido is None:
            return ""

        if isinstance(contenido, str):
            return " ".join(
                contenido.lower().split()
            )

        return " ".join(
            str(contenido).lower().split()
        )

    # ======================================================
    # SERIALIZAR CONTENIDO
    # ======================================================

    @staticmethod
    def _convertir_contenido(
        contenido: Any
    ) -> str:

        if contenido is None:
            return ""

        if isinstance(contenido, str):
            return contenido.strip()

        if isinstance(contenido, dict):

            partes = []

            for clave, valor in contenido.items():

                partes.append(
                    f"{clave}: {valor}"
                )

            return "\n".join(partes)

        if isinstance(contenido, list):

            return "\n".join(
                str(elemento)
                for elemento in contenido
            )

        return str(contenido)

    # ======================================================
    # OBTENER TAREAS RECHAZADAS
    # ======================================================

    @staticmethod
    def _obtener_tareas_rechazadas(
        dictamen_supervisor: Optional[
            Dict[str, Any]
        ]
    ) -> set:

        rechazadas = set()

        if not dictamen_supervisor:
            return rechazadas

        auditorias = dictamen_supervisor.get(
            "auditorias",
            []
        )

        for auditoria in auditorias:

            if not auditoria.get(
                "aprobado",
                False
            ):

                tarea = auditoria.get(
                    "tarea"
                )

                if tarea:
                    rechazadas.add(tarea)

        return rechazadas

    # ======================================================
    # VALIDAR DICTAMEN
    # ======================================================

    def _validar_dictamen(
        self,
        dictamen_supervisor: Optional[
            Dict[str, Any]
        ]
    ):

        if dictamen_supervisor is None:

            raise ValueError(
                "Se necesita el dictamen del supervisor "
                "antes de integrar los resultados."
            )

        listo = dictamen_supervisor.get(
            "listo_para_integrar",
            False
        )

        if (
            not listo
            and not self.permitir_integracion_parcial
        ):

            raise ValueError(
                "El supervisor no aprobó los resultados "
                "para integración."
            )

    # ======================================================
    # ORDENAR RESULTADOS
    # ======================================================

    @staticmethod
    def _ordenar_resultados(
        resultados: List[Dict[str, Any]],
        orden_tareas: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:

        if not orden_tareas:
            return list(resultados)

        posiciones = {
            nombre: indice
            for indice, nombre
            in enumerate(orden_tareas)
        }

        posicion_final = len(
            posiciones
        )

        return sorted(
            resultados,
            key=lambda resultado: posiciones.get(
                resultado.get("tarea"),
                posicion_final
            )
        )

    # ======================================================
    # FILTRAR RESULTADOS VALIDOS
    # ======================================================

    def _filtrar_resultados(
        self,
        resultados: List[Dict[str, Any]],
        dictamen_supervisor: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        tareas_rechazadas = (
            self._obtener_tareas_rechazadas(
                dictamen_supervisor
            )
        )

        resultados_validos = []
        contenidos_vistos = set()

        for resultado in resultados:

            if not isinstance(resultado, dict):
                continue

            tarea = resultado.get("tarea")
            estado = resultado.get("estado")
            contenido = resultado.get("resultado")

            if estado != "completada":
                continue

            if tarea in tareas_rechazadas:
                continue

            contenido_normalizado = (
                self._normalizar_texto(
                    contenido
                )
            )

            if not contenido_normalizado:
                continue

            if contenido_normalizado in contenidos_vistos:
                continue

            contenidos_vistos.add(
                contenido_normalizado
            )

            resultados_validos.append(
                resultado
            )

        return resultados_validos

    # ======================================================
    # CREAR SECCIONES
    # ======================================================

    def _crear_secciones(
        self,
        resultados: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        secciones = []

        for resultado in resultados:

            tarea = resultado.get(
                "tarea",
                "tarea_sin_nombre"
            )

            agente = resultado.get(
                "agente",
                "agente_desconocido"
            )

            contenido = self._convertir_contenido(
                resultado.get("resultado")
            )

            secciones.append(
                {
                    "titulo": tarea,
                    "agente": agente,
                    "contenido": contenido
                }
            )

        return secciones

    # ======================================================
    # CREAR SALIDA DE TEXTO
    # ======================================================

    @staticmethod
    def _crear_salida_texto(
        titulo: str,
        secciones: List[Dict[str, Any]]
    ) -> str:

        partes = [
            f"# {titulo}"
        ]

        for seccion in secciones:

            partes.append(
                f"\n## {seccion['titulo']}"
            )

            partes.append(
                f"Agente responsable: "
                f"{seccion['agente']}"
            )

            partes.append(
                seccion["contenido"]
            )

        return "\n\n".join(partes)

    # ======================================================
    # INTEGRAR
    # ======================================================

    def integrar(
        self,
        resultados: List[Dict[str, Any]],
        dictamen_supervisor: Dict[str, Any],
        titulo: str = "Resultado integrado",
        orden_tareas: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        if resultados is None:
            resultados = []

        self._validar_dictamen(
            dictamen_supervisor
        )

        resultados_validos = (
            self._filtrar_resultados(
                resultados,
                dictamen_supervisor
            )
        )

        resultados_ordenados = (
            self._ordenar_resultados(
                resultados_validos,
                orden_tareas
            )
        )

        secciones = self._crear_secciones(
            resultados_ordenados
        )

        if (
            not secciones
            and not self.permitir_integracion_parcial
        ):

            raise ValueError(
                "No existen resultados aprobados "
                "para integrar."
            )

        salida_texto = self._crear_salida_texto(
            titulo,
            secciones
        )

        estado = (
            "completa"
            if dictamen_supervisor.get(
                "listo_para_integrar",
                False
            )
            else "parcial"
        )

        return {
            "titulo": titulo,
            "estado": estado,
            "fecha_integracion":
                datetime.now().isoformat(
                    timespec="seconds"
                ),
            "total_resultados_recibidos":
                len(resultados),
            "total_resultados_integrados":
                len(secciones),
            "secciones": secciones,
            "salida_final": salida_texto
        }

    # ======================================================
    # INTEGRAR Y GUARDAR EN WORKSPACE
    # ======================================================

    def integrar_y_guardar(
        self,
        resultados: List[Dict[str, Any]],
        dictamen_supervisor: Dict[str, Any],
        workspace,
        titulo: str = "Resultado integrado",
        orden_tareas: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        integracion = self.integrar(
            resultados=resultados,
            dictamen_supervisor=dictamen_supervisor,
            titulo=titulo,
            orden_tareas=orden_tareas
        )

        workspace.guardar(
            "ultima_integracion",
            integracion
        )

        workspace.guardar(
            "salida_final",
            integracion["salida_final"]
        )

        try:
            workspace.guardar_disco()
        except Exception:
            pass

        return integracion


# Nombre alternativo compatible
IntegradorResultados = Integrador
