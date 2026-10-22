# ==========================================================
# DRAYMSYSTEM IA
# MOTOR DE RAZONAMIENTO
# ==========================================================

from datetime import datetime
from typing import Any, Dict, List, Optional


class MotorRazonamiento:
    """
    Motor de razonamiento estructurado de DraymSystem IA.

    Responsabilidades:
    - Analizar objetivos.
    - Detectar restricciones y riesgos.
    - Comparar opciones.
    - Evaluar alternativas mediante criterios ponderados.
    - Recomendar una decisión explicable.
    - Incorporar aprendizaje previo.
    - Compartir conclusiones con el workspace.

    Este módulo no ejecuta agentes, no planifica subtareas y no
    genera lenguaje mediante Transformer. Produce decisiones
    estructuradas para que el orquestador pueda utilizarlas.
    """

    VERSION = "1.0"

    NIVELES_RIESGO = {
        "bajo": 1,
        "medio": 2,
        "alto": 3,
        "critico": 4
    }

    def __init__(
        self,
        aprendizaje=None
    ):

        self.aprendizaje = aprendizaje
        self.historial: List[
            Dict[str, Any]
        ] = []

    # ======================================================
    # FECHA ACTUAL
    # ======================================================

    @staticmethod
    def _fecha_actual() -> str:

        return datetime.now().isoformat(
            timespec="seconds"
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

        return " ".join(
            str(contenido).lower().split()
        )

    # ======================================================
    # NORMALIZAR LISTA
    # ======================================================

    @staticmethod
    def _normalizar_lista(
        elementos: Optional[List[Any]]
    ) -> List[Any]:

        if elementos is None:
            return []

        if isinstance(elementos, list):
            return elementos

        return [elementos]

    # ======================================================
    # CREAR IDENTIFICADOR
    # ======================================================

    def _crear_identificador(self) -> str:

        return (
            f"razonamiento_"
            f"{len(self.historial) + 1}"
        )

    # ======================================================
    # OBTENER APRENDIZAJE ANTERIOR
    # ======================================================

    def _obtener_aprendizaje(
        self,
        objetivo: str,
        limite: int = 5
    ) -> Dict[str, Any]:

        if self.aprendizaje is None:

            return {
                "correcciones_relevantes": [],
                "patrones_relevantes": []
            }

        try:

            return (
                self.aprendizaje
                .crear_contexto_aprendido(
                    objetivo,
                    limite
                )
            )

        except Exception:

            return {
                "correcciones_relevantes": [],
                "patrones_relevantes": []
            }

    # ======================================================
    # ANALIZAR OBJETIVO
    # ======================================================

    def analizar_objetivo(
        self,
        objetivo: str,
        contexto: Optional[
            Dict[str, Any]
        ] = None,
        restricciones: Optional[
            List[str]
        ] = None
    ) -> Dict[str, Any]:

        objetivo_limpio = str(
            objetivo or ""
        ).strip()

        if not objetivo_limpio:

            raise ValueError(
                "El objetivo no puede estar vacío."
            )

        contexto = contexto or {}

        restricciones = self._normalizar_lista(
            restricciones
        )

        palabras = objetivo_limpio.split()

        complejidad = self._estimar_complejidad(
            objetivo_limpio,
            restricciones,
            contexto
        )

        aprendizaje_previo = (
            self._obtener_aprendizaje(
                objetivo_limpio
            )
        )

        return {
            "objetivo": objetivo_limpio,
            "cantidad_palabras":
                len(palabras),
            "restricciones":
                restricciones,
            "contexto_disponible":
                list(contexto.keys()),
            "complejidad_estimada":
                complejidad,
            "aprendizaje_previo":
                aprendizaje_previo
        }

    # ======================================================
    # ESTIMAR COMPLEJIDAD
    # ======================================================

    def _estimar_complejidad(
        self,
        objetivo: str,
        restricciones: List[str],
        contexto: Dict[str, Any]
    ) -> str:

        puntuacion = 0

        cantidad_palabras = len(
            objetivo.split()
        )

        if cantidad_palabras >= 20:
            puntuacion += 1

        if cantidad_palabras >= 50:
            puntuacion += 1

        if len(restricciones) >= 2:
            puntuacion += 1

        if len(restricciones) >= 5:
            puntuacion += 1

        if len(contexto) >= 5:
            puntuacion += 1

        palabras_complejas = {
            "arquitectura",
            "sistema",
            "completo",
            "multiagente",
            "integración",
            "seguridad",
            "distribuido",
            "autónomo",
            "optimización",
            "sistema operativo"
        }

        objetivo_normalizado = (
            self._normalizar_texto(
                objetivo
            )
        )

        coincidencias = sum(
            1
            for palabra in palabras_complejas
            if palabra in objetivo_normalizado
        )

        puntuacion += min(
            coincidencias,
            3
        )

        if puntuacion <= 1:
            return "baja"

        if puntuacion <= 3:
            return "media"

        if puntuacion <= 5:
            return "alta"

        return "muy_alta"

    # ======================================================
    # ANALIZAR RIESGOS
    # ======================================================

    def analizar_riesgos(
        self,
        objetivo: str,
        restricciones: Optional[
            List[str]
        ] = None,
        riesgos_adicionales: Optional[
            List[Dict[str, Any]]
        ] = None
    ) -> List[Dict[str, Any]]:

        restricciones = self._normalizar_lista(
            restricciones
        )

        riesgos = []

        if not restricciones:

            riesgos.append(
                {
                    "codigo":
                        "RESTRICCIONES_NO_DEFINIDAS",
                    "descripcion": (
                        "El objetivo no contiene "
                        "restricciones explícitas."
                    ),
                    "nivel": "medio",
                    "puntuacion": 2
                }
            )

        objetivo_normalizado = (
            self._normalizar_texto(
                objetivo
            )
        )

        indicadores = {
            "seguridad": (
                "El objetivo requiere revisar "
                "aspectos de seguridad."
            ),
            "eliminar": (
                "El objetivo podría implicar "
                "pérdida de información."
            ),
            "reemplazar": (
                "El objetivo podría modificar "
                "componentes existentes."
            ),
            "paralelo": (
                "La ejecución paralela puede "
                "producir conflictos."
            ),
            "autónomo": (
                "La autonomía requiere límites "
                "y supervisión explícitos."
            )
        }

        for indicador, descripcion in (
            indicadores.items()
        ):

            if indicador in objetivo_normalizado:

                riesgos.append(
                    {
                        "codigo": (
                            f"RIESGO_"
                            f"{indicador.upper()}"
                        ),
                        "descripcion": descripcion,
                        "nivel": "medio",
                        "puntuacion": 2
                    }
                )

        if riesgos_adicionales:

            for riesgo in riesgos_adicionales:

                if not isinstance(
                    riesgo,
                    dict
                ):
                    continue

                nivel = riesgo.get(
                    "nivel",
                    "medio"
                )

                riesgos.append(
                    {
                        "codigo": riesgo.get(
                            "codigo",
                            "RIESGO_ADICIONAL"
                        ),
                        "descripcion": riesgo.get(
                            "descripcion",
                            "Riesgo no especificado."
                        ),
                        "nivel": nivel,
                        "puntuacion":
                            self.NIVELES_RIESGO.get(
                                nivel,
                                2
                            )
                    }
                )

        return riesgos

    # ======================================================
    # VALIDAR CRITERIOS
    # ======================================================

    @staticmethod
    def _validar_criterios(
        criterios: Dict[str, float]
    ) -> Dict[str, float]:

        if not criterios:

            raise ValueError(
                "Se necesita al menos un criterio."
            )

        criterios_validos = {}

        for nombre, peso in criterios.items():

            try:
                peso_numerico = float(
                    peso
                )
            except (
                TypeError,
                ValueError
            ):
                continue

            if peso_numerico > 0:

                criterios_validos[
                    str(nombre)
                ] = peso_numerico

        if not criterios_validos:

            raise ValueError(
                "Los criterios no contienen "
                "pesos válidos."
            )

        total_pesos = sum(
            criterios_validos.values()
        )

        return {
            nombre: peso / total_pesos
            for nombre, peso
            in criterios_validos.items()
        }

    # ======================================================
    # EVALUAR UNA OPCION
    # ======================================================

    def evaluar_opcion(
        self,
        opcion: Dict[str, Any],
        criterios: Dict[str, float]
    ) -> Dict[str, Any]:

        nombre = opcion.get(
            "nombre"
        )

        if not nombre:

            raise ValueError(
                "Cada opción necesita un nombre."
            )

        valores = opcion.get(
            "criterios",
            {}
        )

        puntuacion_total = 0.0
        desglose = {}

        for criterio, peso in criterios.items():

            valor = valores.get(
                criterio,
                0
            )

            try:
                valor_numerico = float(
                    valor
                )
            except (
                TypeError,
                ValueError
            ):
                valor_numerico = 0.0

            valor_numerico = max(
                0.0,
                min(
                    10.0,
                    valor_numerico
                )
            )

            aportacion = (
                valor_numerico * peso
            )

            puntuacion_total += aportacion

            desglose[criterio] = {
                "valor": valor_numerico,
                "peso": round(
                    peso,
                    4
                ),
                "aportacion": round(
                    aportacion,
                    4
                )
            }

        penalizacion_riesgo = self._calcular_penalizacion(
            opcion.get(
                "riesgos",
                []
            )
        )

        puntuacion_final = max(
            0.0,
            puntuacion_total
            - penalizacion_riesgo
        )

        return {
            "nombre": nombre,
            "descripcion": opcion.get(
                "descripcion",
                ""
            ),
            "puntuacion_base": round(
                puntuacion_total,
                4
            ),
            "penalizacion_riesgo": round(
                penalizacion_riesgo,
                4
            ),
            "puntuacion_final": round(
                puntuacion_final,
                4
            ),
            "desglose": desglose,
            "riesgos": opcion.get(
                "riesgos",
                []
            ),
            "datos_originales": opcion
        }

    # ======================================================
    # CALCULAR PENALIZACION POR RIESGO
    # ======================================================

    def _calcular_penalizacion(
        self,
        riesgos: List[Any]
    ) -> float:

        penalizacion = 0.0

        for riesgo in riesgos:

            if isinstance(riesgo, str):

                nivel = riesgo.lower()

            elif isinstance(riesgo, dict):

                nivel = str(
                    riesgo.get(
                        "nivel",
                        "medio"
                    )
                ).lower()

            else:
                continue

            puntuacion = (
                self.NIVELES_RIESGO.get(
                    nivel,
                    2
                )
            )

            penalizacion += (
                puntuacion * 0.15
            )

        return penalizacion

    # ======================================================
    # COMPARAR OPCIONES
    # ======================================================

    def comparar_opciones(
        self,
        opciones: List[Dict[str, Any]],
        criterios: Dict[str, float]
    ) -> Dict[str, Any]:

        if not opciones:

            raise ValueError(
                "Se necesita al menos una opción."
            )

        criterios_normalizados = (
            self._validar_criterios(
                criterios
            )
        )

        evaluaciones = [
            self.evaluar_opcion(
                opcion,
                criterios_normalizados
            )
            for opcion in opciones
        ]

        evaluaciones.sort(
            key=lambda evaluacion:
                evaluacion[
                    "puntuacion_final"
                ],
            reverse=True
        )

        mejor_opcion = evaluaciones[0]

        diferencia = 0.0

        if len(evaluaciones) > 1:

            diferencia = (
                mejor_opcion[
                    "puntuacion_final"
                ]
                - evaluaciones[1][
                    "puntuacion_final"
                ]
            )

        confianza = self._calcular_confianza(
            mejor_opcion[
                "puntuacion_final"
            ],
            diferencia,
            len(evaluaciones)
        )

        return {
            "criterios":
                criterios_normalizados,
            "clasificacion":
                evaluaciones,
            "mejor_opcion":
                mejor_opcion,
            "confianza":
                confianza
        }

    # ======================================================
    # CALCULAR CONFIANZA
    # ======================================================

    @staticmethod
    def _calcular_confianza(
        puntuacion: float,
        diferencia: float,
        cantidad_opciones: int
    ) -> Dict[str, Any]:

        base = max(
            0.0,
            min(
                1.0,
                puntuacion / 10.0
            )
        )

        separacion = max(
            0.0,
            min(
                1.0,
                diferencia / 3.0
            )
        )

        valor = (
            base * 0.7
            + separacion * 0.3
        )

        if cantidad_opciones == 1:
            valor = min(
                valor,
                0.6
            )

        if valor >= 0.75:
            nivel = "alta"

        elif valor >= 0.45:
            nivel = "media"

        else:
            nivel = "baja"

        return {
            "valor": round(
                valor,
                4
            ),
            "nivel": nivel
        }

    # ======================================================
    # GENERAR EXPLICACION
    # ======================================================

    @staticmethod
    def _generar_explicacion(
        comparacion: Dict[str, Any]
    ) -> str:

        mejor = comparacion.get(
            "mejor_opcion",
            {}
        )

        nombre = mejor.get(
            "nombre",
            "opción desconocida"
        )

        puntuacion = mejor.get(
            "puntuacion_final",
            0
        )

        confianza = comparacion.get(
            "confianza",
            {}
        ).get(
            "nivel",
            "baja"
        )

        return (
            f"La opción recomendada es '{nombre}' "
            f"con una puntuación de "
            f"{puntuacion:.2f} sobre 10. "
            f"El nivel de confianza es "
            f"{confianza}."
        )

    # ======================================================
    # RAZONAR
    # ======================================================

    def razonar(
        self,
        objetivo: str,
        opciones: List[Dict[str, Any]],
        criterios: Dict[str, float],
        contexto: Optional[
            Dict[str, Any]
        ] = None,
        restricciones: Optional[
            List[str]
        ] = None,
        riesgos_adicionales: Optional[
            List[Dict[str, Any]]
        ] = None,
        proyecto: str = "general"
    ) -> Dict[str, Any]:

        analisis = self.analizar_objetivo(
            objetivo=objetivo,
            contexto=contexto,
            restricciones=restricciones
        )

        riesgos = self.analizar_riesgos(
            objetivo=objetivo,
            restricciones=restricciones,
            riesgos_adicionales=(
                riesgos_adicionales
            )
        )

        comparacion = (
            self.comparar_opciones(
                opciones=opciones,
                criterios=criterios
            )
        )

        mejor_opcion = comparacion[
            "mejor_opcion"
        ]

        registro = {
            "id":
                self._crear_identificador(),
            "fecha":
                self._fecha_actual(),
            "version":
                self.VERSION,
            "proyecto":
                proyecto,
            "objetivo":
                objetivo,
            "analisis":
                analisis,
            "riesgos_generales":
                riesgos,
            "comparacion":
                comparacion,
            "decision_recomendada":
                mejor_opcion.get(
                    "nombre"
                ),
            "explicacion":
                self._generar_explicacion(
                    comparacion
                )
        }

        self.historial.append(
            registro
        )

        self._registrar_aprendizaje(
            registro
        )

        return registro

    # ======================================================
    # REGISTRAR DECISION EN APRENDIZAJE
    # ======================================================

    def _registrar_aprendizaje(
        self,
        razonamiento: Dict[str, Any]
    ):

        if self.aprendizaje is None:
            return

        try:

            self.aprendizaje.registrar_decision(
                decision=razonamiento.get(
                    "decision_recomendada",
                    ""
                ),
                contexto={
                    "objetivo":
                        razonamiento.get(
                            "objetivo"
                        ),
                    "analisis":
                        razonamiento.get(
                            "analisis"
                        ),
                    "riesgos":
                        razonamiento.get(
                            "riesgos_generales"
                        )
                },
                resultado=razonamiento.get(
                    "comparacion"
                ),
                proyecto=razonamiento.get(
                    "proyecto",
                    "general"
                )
            )

        except Exception:
            pass

    # ======================================================
    # RAZONAR Y GUARDAR EN WORKSPACE
    # ======================================================

    def razonar_y_guardar(
        self,
        objetivo: str,
        opciones: List[Dict[str, Any]],
        criterios: Dict[str, float],
        workspace,
        contexto: Optional[
            Dict[str, Any]
        ] = None,
        restricciones: Optional[
            List[str]
        ] = None,
        riesgos_adicionales: Optional[
            List[Dict[str, Any]]
        ] = None,
        proyecto: str = "general"
    ) -> Dict[str, Any]:

        resultado = self.razonar(
            objetivo=objetivo,
            opciones=opciones,
            criterios=criterios,
            contexto=contexto,
            restricciones=restricciones,
            riesgos_adicionales=(
                riesgos_adicionales
            ),
            proyecto=proyecto
        )

        workspace.guardar(
            "ultimo_razonamiento",
            resultado
        )

        workspace.guardar(
            "decision_recomendada",
            resultado[
                "decision_recomendada"
            ]
        )

        try:
            workspace.guardar_disco()
        except Exception:
            pass

        return resultado

    # ======================================================
    # OBTENER HISTORIAL
    # ======================================================

    def obtener_historial(
        self
    ) -> List[Dict[str, Any]]:

        return list(
            self.historial
        )

    # ======================================================
    # OBTENER ULTIMO RAZONAMIENTO
    # ======================================================

    def obtener_ultimo(
        self
    ) -> Optional[Dict[str, Any]]:

        if not self.historial:
            return None

        return self.historial[-1]


# Nombre alternativo compatible
Razonamiento = MotorRazonamiento
