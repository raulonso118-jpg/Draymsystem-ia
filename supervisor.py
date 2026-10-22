# ==========================================================
# DRAYMSYSTEM IA
# SUPERVISOR DE RESULTADOS
# ==========================================================

from typing import Any, Dict, List, Optional


class Supervisor:
    """
    Revisa los resultados producidos por el enjambre.

    Responsabilidades:
    - Detectar errores.
    - Detectar resultados vacíos o insuficientes.
    - Detectar tareas incompletas.
    - Detectar resultados duplicados.
    - Determinar si los resultados pueden integrarse.

    El supervisor no ejecuta agentes ni modifica resultados.
    Solo revisa y emite un dictamen.
    """

    def __init__(self, longitud_minima: int = 10):

        self.longitud_minima = max(
            1,
            int(longitud_minima)
        )

    # ======================================================
    # NORMALIZAR CONTENIDO
    # ======================================================

    @staticmethod
    def _normalizar_texto(contenido: Any) -> str:

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
    # CREAR OBSERVACION
    # ======================================================

    @staticmethod
    def _crear_observacion(
        codigo: str,
        mensaje: str,
        gravedad: str = "advertencia"
    ) -> Dict[str, str]:

        return {
            "codigo": codigo,
            "mensaje": mensaje,
            "gravedad": gravedad
        }

    # ======================================================
    # VALIDAR ESTRUCTURA
    # ======================================================

    def validar_estructura(
        self,
        resultado: Any
    ) -> List[Dict[str, str]]:

        observaciones = []

        if not isinstance(resultado, dict):

            observaciones.append(
                self._crear_observacion(
                    codigo="ESTRUCTURA_INVALIDA",
                    mensaje=(
                        "El resultado debe ser "
                        "un diccionario."
                    ),
                    gravedad="critica"
                )
            )

            return observaciones

        campos_requeridos = [
            "tarea",
            "agente",
            "estado",
            "resultado",
            "error"
        ]

        for campo in campos_requeridos:

            if campo not in resultado:

                observaciones.append(
                    self._crear_observacion(
                        codigo="CAMPO_FALTANTE",
                        mensaje=(
                            f"Falta el campo obligatorio: "
                            f"{campo}."
                        ),
                        gravedad="critica"
                    )
                )

        return observaciones

    # ======================================================
    # DETECTAR ERRORES
    # ======================================================

    def detectar_errores(
        self,
        resultado: Dict[str, Any]
    ) -> List[Dict[str, str]]:

        observaciones = []

        estado = resultado.get("estado")
        error = resultado.get("error")

        if estado == "fallida":

            observaciones.append(
                self._crear_observacion(
                    codigo="TAREA_FALLIDA",
                    mensaje=(
                        "La tarea fue marcada "
                        "como fallida."
                    ),
                    gravedad="critica"
                )
            )

        if error:

            observaciones.append(
                self._crear_observacion(
                    codigo="ERROR_REPORTADO",
                    mensaje=(
                        f"El agente reportó un error: "
                        f"{error}"
                    ),
                    gravedad="critica"
                )
            )

        return observaciones

    # ======================================================
    # DETECTAR RESULTADO VACIO
    # ======================================================

    def detectar_resultado_vacio(
        self,
        resultado: Dict[str, Any]
    ) -> List[Dict[str, str]]:

        observaciones = []

        contenido = resultado.get("resultado")

        if contenido is None:

            observaciones.append(
                self._crear_observacion(
                    codigo="RESULTADO_VACIO",
                    mensaje=(
                        "La tarea no produjo "
                        "ningún resultado."
                    ),
                    gravedad="critica"
                )
            )

            return observaciones

        texto = self._normalizar_texto(
            contenido
        )

        if not texto:

            observaciones.append(
                self._crear_observacion(
                    codigo="RESULTADO_VACIO",
                    mensaje=(
                        "El resultado no contiene "
                        "información útil."
                    ),
                    gravedad="critica"
                )
            )

        elif len(texto) < self.longitud_minima:

            observaciones.append(
                self._crear_observacion(
                    codigo="RESULTADO_INSUFICIENTE",
                    mensaje=(
                        "El resultado es demasiado corto "
                        "para considerarse completo."
                    ),
                    gravedad="advertencia"
                )
            )

        return observaciones

    # ======================================================
    # DETECTAR DATOS INCOMPLETOS
    # ======================================================

    def detectar_datos_incompletos(
        self,
        resultado: Dict[str, Any]
    ) -> List[Dict[str, str]]:

        observaciones = []

        if not resultado.get("tarea"):

            observaciones.append(
                self._crear_observacion(
                    codigo="TAREA_SIN_NOMBRE",
                    mensaje=(
                        "El resultado no identifica "
                        "la tarea ejecutada."
                    ),
                    gravedad="critica"
                )
            )

        if not resultado.get("agente"):

            observaciones.append(
                self._crear_observacion(
                    codigo="AGENTE_NO_IDENTIFICADO",
                    mensaje=(
                        "El resultado no identifica "
                        "al agente responsable."
                    ),
                    gravedad="advertencia"
                )
            )

        estado = resultado.get("estado")

        estados_validos = {
            "completada",
            "fallida"
        }

        if estado not in estados_validos:

            observaciones.append(
                self._crear_observacion(
                    codigo="ESTADO_INVALIDO",
                    mensaje=(
                        f"El estado '{estado}' "
                        "no es reconocido."
                    ),
                    gravedad="critica"
                )
            )

        return observaciones

    # ======================================================
    # AUDITAR UN RESULTADO
    # ======================================================

    def auditar_resultado(
        self,
        resultado: Any
    ) -> Dict[str, Any]:

        observaciones = self.validar_estructura(
            resultado
        )

        if not isinstance(resultado, dict):

            return {
                "tarea": "desconocida",
                "agente": None,
                "aprobado": False,
                "requiere_correccion": True,
                "observaciones": observaciones
            }

        observaciones.extend(
            self.detectar_errores(
                resultado
            )
        )

        observaciones.extend(
            self.detectar_resultado_vacio(
                resultado
            )
        )

        observaciones.extend(
            self.detectar_datos_incompletos(
                resultado
            )
        )

        tiene_errores_criticos = any(
            observacion.get("gravedad") == "critica"
            for observacion in observaciones
        )

        return {
            "tarea": resultado.get(
                "tarea",
                "desconocida"
            ),
            "agente": resultado.get("agente"),
            "aprobado": not tiene_errores_criticos,
            "requiere_correccion":
                tiene_errores_criticos,
            "observaciones": observaciones
        }

    # ======================================================
    # DETECTAR DUPLICADOS
    # ======================================================

    def detectar_duplicados(
        self,
        resultados: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        duplicados = []
        contenidos_vistos = {}

        for resultado in resultados:

            if not isinstance(resultado, dict):
                continue

            contenido = self._normalizar_texto(
                resultado.get("resultado")
            )

            if not contenido:
                continue

            tarea_actual = resultado.get(
                "tarea",
                "desconocida"
            )

            if contenido in contenidos_vistos:

                duplicados.append(
                    {
                        "tarea": tarea_actual,
                        "duplicada_de":
                            contenidos_vistos[
                                contenido
                            ],
                        "codigo":
                            "RESULTADO_DUPLICADO",
                        "mensaje": (
                            "Dos tareas produjeron "
                            "el mismo contenido."
                        ),
                        "gravedad": "advertencia"
                    }
                )

            else:

                contenidos_vistos[
                    contenido
                ] = tarea_actual

        return duplicados

    # ======================================================
    # DETECTAR TAREAS FALTANTES
    # ======================================================

    @staticmethod
    def detectar_tareas_faltantes(
        resultados: List[Dict[str, Any]],
        tareas_esperadas: Optional[List[str]] = None
    ) -> List[str]:

        if not tareas_esperadas:
            return []

        tareas_recibidas = {
            resultado.get("tarea")
            for resultado in resultados
            if isinstance(resultado, dict)
        }

        return [
            tarea
            for tarea in tareas_esperadas
            if tarea not in tareas_recibidas
        ]

    # ======================================================
    # SUPERVISAR EJECUCION COMPLETA
    # ======================================================

    def supervisar(
        self,
        resultados: List[Dict[str, Any]],
        tareas_esperadas: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        if resultados is None:
            resultados = []

        auditorias = [
            self.auditar_resultado(resultado)
            for resultado in resultados
        ]

        duplicados = self.detectar_duplicados(
            resultados
        )

        tareas_faltantes = (
            self.detectar_tareas_faltantes(
                resultados,
                tareas_esperadas
            )
        )

        auditorias_aprobadas = [
            auditoria
            for auditoria in auditorias
            if auditoria["aprobado"]
        ]

        auditorias_rechazadas = [
            auditoria
            for auditoria in auditorias
            if not auditoria["aprobado"]
        ]

        listo_para_integrar = (
            len(resultados) > 0
            and not auditorias_rechazadas
            and not tareas_faltantes
        )

        return {
            "estado": (
                "aprobado"
                if listo_para_integrar
                else "requiere_correccion"
            ),
            "listo_para_integrar":
                listo_para_integrar,
            "total_resultados":
                len(resultados),
            "resultados_aprobados":
                len(auditorias_aprobadas),
            "resultados_rechazados":
                len(auditorias_rechazadas),
            "auditorias": auditorias,
            "duplicados": duplicados,
            "tareas_faltantes":
                tareas_faltantes
        }

    # ======================================================
    # SUPERVISAR Y GUARDAR EN WORKSPACE
    # ======================================================

    def supervisar_y_guardar(
        self,
        resultados: List[Dict[str, Any]],
        workspace,
        tareas_esperadas: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        dictamen = self.supervisar(
            resultados,
            tareas_esperadas
        )

        workspace.guardar(
            "ultimo_dictamen_supervisor",
            dictamen
        )

        try:
            workspace.guardar_disco()
        except Exception:
            pass

        return dictamen


# Nombre alternativo compatible
SupervisorResultados = Supervisor
