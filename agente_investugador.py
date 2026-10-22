# ==========================================================
# DRAYMSYSTEM IA
# AGENTE INVESTIGADOR
# INVESTIGACIÓN, EVIDENCIA Y ANÁLISIS DE FUENTES
# ==========================================================

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from agentes.agente_general import AgenteGeneral


class AgenteInvestigador(AgenteGeneral):

    INTENT_TAG = "investigacion"

    AGENT_LEVEL = 4

    ROLE = "researcher"

    VERSION = "2.0.0"

    SPECIALTIES = [
        "investigacion",
        "busqueda",
        "fuentes",
        "evidencia",
        "documentacion",
        "analisis",
        "comparacion",
        "verificacion",
        "contraste",
        "sintesis",
        "referencias",
        "trazabilidad"
    ]

    PALABRAS_CLAVE = {
        "investigar",
        "investigacion",
        "buscar",
        "busqueda",
        "fuente",
        "fuentes",
        "evidencia",
        "referencia",
        "referencias",
        "analizar",
        "analisis",
        "comparar",
        "comparacion",
        "contrastar",
        "verificar",
        "comprobar",
        "documentar",
        "hallazgo",
        "hallazgos",
        "estudio",
        "reporte",
        "informe"
    }

    TIPOS_FUENTE_VALIDOS = {
        "documento",
        "archivo",
        "libro",
        "articulo",
        "informe",
        "base_datos",
        "sitio_web",
        "correo",
        "chat",
        "reunion",
        "codigo",
        "usuario",
        "sistema",
        "desconocida"
    }

    NIVELES_CONFIANZA = {
        "muy_baja": 0.20,
        "baja": 0.40,
        "media": 0.60,
        "alta": 0.80,
        "muy_alta": 1.00
    }

    def __init__(self):

        super().__init__()

        self.fecha_creacion = (
            datetime.now()
        )

        self.total_investigaciones = 0

        self.total_fuentes_procesadas = 0

        self.total_hallazgos = 0

        self.ultima_investigacion = None

        self.historial = []

    # ======================================================
    # UTILIDADES INTERNAS
    # ======================================================

    def _normalizar_texto(
        self,
        contenido
    ) -> str:

        if contenido is None:
            return ""

        return str(
            contenido
        ).strip()

    def _eliminar_duplicados(
        self,
        elementos
    ):

        resultado = []

        claves_vistas = set()

        for elemento in elementos:

            if isinstance(
                elemento,
                dict
            ):

                clave = (
                    elemento.get("titulo"),
                    elemento.get("contenido"),
                    elemento.get("url"),
                    elemento.get("afirmacion")
                )

            else:

                clave = self._normalizar_texto(
                    elemento
                ).lower()

            if clave not in claves_vistas:

                claves_vistas.add(
                    clave
                )

                resultado.append(
                    elemento
                )

        return resultado

    def _limitar_valor(
        self,
        valor,
        minimo=0.0,
        maximo=1.0
    ) -> float:

        try:

            numero = float(
                valor
            )

        except (
            TypeError,
            ValueError
        ):

            numero = minimo

        return max(
            minimo,
            min(
                maximo,
                numero
            )
        )

    def _obtener_dominio(
        self,
        url
    ) -> Optionaltexto = self._normalizar_texto(
            url
        )

        if not texto:
            return None

        try:

            resultado = urlparse(
                texto
            )

            return (
                resultado.netloc
                or None
            )

        except ValueError:

            return None

    # ======================================================
    # CAPACIDAD
    # ======================================================

    def puede_resolver(
        self,
        tarea
    ) -> bool:

        texto = self._normalizar_texto(
            tarea
        ).lower()

        return any(
            palabra in texto
            for palabra in self.PALABRAS_CLAVE
        )

    # ======================================================
    # CREAR FUENTE
    # ======================================================

    def crear_fuente(
        self,
        titulo,
        contenido=None,
        tipo="desconocida",
        autor=None,
        fecha=None,
        url=None,
        origen=None,
        confiabilidad=None,
        metadatos=None
    ) -> Dict[str, Any]:

        tipo_normalizado = (
            self._normalizar_texto(
                tipo
            ).lower()
            or "desconocida"
        )

        if (
            tipo_normalizado
            not in self.TIPOS_FUENTE_VALIDOS
        ):

            tipo_normalizado = (
                "desconocida"
            )

        fuente = {
            "titulo":
                self._normalizar_texto(
                    titulo
                )
                or "Fuente sin título",

            "contenido":
                self._normalizar_texto(
                    contenido
                ),

            "tipo":
                tipo_normalizado,

            "autor":
                self._normalizar_texto(
                    autor
                )
                or None,

            "fecha":
                self._normalizar_texto(
                    fecha
                )
                or None,

            "url":
                self._normalizar_texto(
                    url
                )
                or None,

            "dominio":
                self._obtener_dominio(
                    url
                ),

            "origen":
                self._normalizar_texto(
                    origen
                )
                or None,

            "confiabilidad_declarada":
                (
                    self._limitar_valor(
                        confiabilidad
                    )
                    if confiabilidad is not None
                    else None
                ),

            "metadatos":
                (
                    dict(metadatos)
                    if isinstance(
                        metadatos,
                        dict
                    )
                    else {}
                )
        }

        fuente["evaluacion"] = (
            self.evaluar_fuente(
                fuente
            )
        )

        return fuente

    # ======================================================
    # NORMALIZAR FUENTES
    # ======================================================

    def normalizar_fuentes(
        self,
        fuentes
    ) -> List[Dict[str, Any]]:

        if fuentes is None:
            return []

        if isinstance(
            fuentes,
            (
                str,
                dict
            )
        ):

            fuentes = [
                fuentes
            ]

        if not isinstance(
            fuentes,
            (
                list,
                tuple,
                set
            )
        ):

            fuentes = [
                fuentes
            ]

        resultado = []

        for indice, fuente in enumerate(
            fuentes,
            start=1
        ):

            if isinstance(
                fuente,
                dict
            ):

                resultado.append(
                    self.crear_fuente(
                        titulo=fuente.get(
                            "titulo",
                            f"Fuente {indice}"
                        ),
                        contenido=fuente.get(
                            "contenido",
                            fuente.get(
                                "texto",
                                fuente.get(
                                    "resumen",
                                    ""
                                )
                            )
                        ),
                        tipo=fuente.get(
                            "tipo",
                            "desconocida"
                        ),
                        autor=fuente.get(
                            "autor"
                        ),
                        fecha=fuente.get(
                            "fecha"
                        ),
                        url=fuente.get(
                            "url"
                        ),
                        origen=fuente.get(
                            "origen"
                        ),
                        confiabilidad=fuente.get(
                            "confiabilidad"
                        ),
                        metadatos=fuente.get(
                            "metadatos"
                        )
                    )
                )

            else:

                resultado.append(
                    self.crear_fuente(
                        titulo=(
                            f"Fuente {indice}"
                        ),
                        contenido=fuente,
                        tipo="desconocida"
                    )
                )

        return self._eliminar_duplicados(
            resultado
        )

    # ======================================================
    # EVALUAR FUENTE
    # ======================================================

    def evaluar_fuente(
        self,
        fuente
    ) -> Dict[str, Any]:

        if not isinstance(
            fuente,
            dict
        ):

            return {
                "puntaje": 0,
                "nivel": "muy_baja",
                "criterios": {},
                "advertencias": [
                    "La fuente no tiene una estructura válida."
                ]
            }

        contenido = self._normalizar_texto(
            fuente.get("contenido")
        )

        titulo = self._normalizar_texto(
            fuente.get("titulo")
        )

        autor = self._normalizar_texto(
            fuente.get("autor")
        )

        fecha = self._normalizar_texto(
            fuente.get("fecha")
        )

        url = self._normalizar_texto(
            fuente.get("url")
        )

        origen = self._normalizar_texto(
            fuente.get("origen")
        )

        confiabilidad_declarada = fuente.get(
            "confiabilidad_declarada"
        )

        criterios = {
            "contenido_disponible":
                1.0 if contenido else 0.0,

            "titulo_disponible":
                1.0 if titulo else 0.0,

            "autor_identificado":
                1.0 if autor else 0.0,

            "fecha_identificada":
                1.0 if fecha else 0.0,

            "origen_identificado":
                1.0
                if (
                    origen
                    or url
                )
                else 0.0,

            "extension_suficiente":
                1.0
                if len(contenido) >= 100
                else (
                    0.5
                    if len(contenido) >= 30
                    else 0.0
                )
        }

        pesos = {
            "contenido_disponible": 0.30,
            "titulo_disponible": 0.10,
            "autor_identificado": 0.15,
            "fecha_identificada": 0.15,
            "origen_identificado": 0.20,
            "extension_suficiente": 0.10
        }

        puntaje_base = sum(
            criterios[criterio]
            * pesos[criterio]
            for criterio in criterios
        )

        if confiabilidad_declarada is not None:

            confiabilidad = (
                self._limitar_valor(
                    confiabilidad_declarada
                )
            )

            puntaje_final = (
                puntaje_base * 0.70
                + confiabilidad * 0.30
            )

        else:

            puntaje_final = (
                puntaje_base
            )

        puntaje = round(
            puntaje_final * 100,
            2
        )

        if puntaje >= 85:
            nivel = "muy_alta"

        elif puntaje >= 70:
            nivel = "alta"

        elif puntaje >= 50:
            nivel = "media"

        elif puntaje >= 30:
            nivel = "baja"

        else:
            nivel = "muy_baja"

        advertencias = []

        if not contenido:

            advertencias.append(
                "La fuente no contiene información analizable."
            )

        if not autor:

            advertencias.append(
                "La fuente no identifica a su autor."
            )

        if not fecha:

            advertencias.append(
                "La fuente no especifica una fecha."
            )

        if not origen and not url:

            advertencias.append(
                "La fuente no identifica su origen."
            )

        if len(contenido) < 30:

            advertencias.append(
                "El contenido disponible es demasiado breve."
            )

        return {
            "puntaje":
                puntaje,

            "nivel":
                nivel,

            "criterios":
                criterios,

            "advertencias":
                advertencias
        }

    # ======================================================
    # PLAN DE INVESTIGACIÓN
    # ======================================================

    def generar_plan(
        self,
        tema,
        objetivo=None,
        preguntas=None
    ) -> Dict[str, Any]:

        tema_normalizado = (
            self._normalizar_texto(
                tema
            )
        )

        objetivo_normalizado = (
            self._normalizar_texto(
                objetivo
            )
        )

        if not objetivo_normalizado:

            objetivo_normalizado = (
                f"Investigar y organizar información "
                f"verificable sobre: {tema_normalizado}."
            )

        if preguntas is None:

            preguntas_normalizadas = [
                (
                    f"¿Qué información verificable existe "
                    f"sobre {tema_normalizado}?"
                ),
                (
                    "¿Qué fuentes respaldan los principales "
                    "hallazgos?"
                ),
                (
                    "¿Existen contradicciones, vacíos o "
                    "limitaciones en la evidencia?"
                )
            ]

        elif isinstance(
            preguntas,
            str
        ):

            preguntas_normalizadas = [
                preguntas
            ]

        else:

            preguntas_normalizadas = [
                self._normalizar_texto(
                    pregunta
                )
                for pregunta in preguntas
                if self._normalizar_texto(
                    pregunta
                )
            ]

        return {
            "tema":
                tema_normalizado,

            "objetivo":
                objetivo_normalizado,

            "preguntas":
                preguntas_normalizadas,

            "etapas": [
                "Definir el alcance de la investigación.",
                "Identificar y reunir fuentes disponibles.",
                "Evaluar la calidad de cada fuente.",
                "Extraer hallazgos relevantes.",
                "Contrastar las afirmaciones encontradas.",
                "Identificar contradicciones y vacíos.",
                "Generar una síntesis trazable."
            ]
        }

    # ======================================================
    # EXTRAER HALLAZGOS
    # ======================================================

    def extraer_hallazgos(
        self,
        fuentes
    ) -> List[Dict[str, Any]]:

        fuentes_normalizadas = (
            self.normalizar_fuentes(
                fuentes
            )
        )

        hallazgos = []

        for indice, fuente in enumerate(
            fuentes_normalizadas,
            start=1
        ):

            contenido = fuente.get(
                "contenido",
                ""
            )

            if not contenido:
                continue

            fragmentos = [
                fragmento.strip()
                for fragmento in contenido.replace(
                    "\n",
                    " "
                ).split(".")
                if fragmento.strip()
            ]

            for posicion, fragmento in enumerate(
                fragmentos,
                start=1
            ):

                if len(fragmento) < 15:
                    continue

                hallazgos.append({
                    "id":
                        (
                            f"H-{indice:03d}-"
                            f"{posicion:03d}"
                        ),

                    "afirmacion":
                        fragmento,

                    "fuente":
                        fuente.get(
                            "titulo"
                        ),

                    "tipo_fuente":
                        fuente.get(
                            "tipo"
                        ),

                    "confiabilidad_fuente":
                        fuente.get(
                            "evaluacion",
                            {}
                        ).get(
                            "nivel",
                            "muy_baja"
                        ),

                    "puntaje_fuente":
                        fuente.get(
                            "evaluacion",
                            {}
                        ).get(
                            "puntaje",
                            0
                        ),

                    "verificado":
                        False,

                    "estado":
                        "pendiente_de_contraste"
                })

        return self._eliminar_duplicados(
            hallazgos
        )

    # ======================================================
    # COMPARAR TEXTOS
    # ======================================================

    def _palabras_significativas(
        self,
        texto
    ):

        palabras_excluidas = {
            "para",
            "como",
            "este",
            "esta",
            "estos",
            "estas",
            "desde",
            "sobre",
            "entre",
            "porque",
            "pero",
            "tambien",
            "tiene",
            "tienen",
            "hacer",
            "puede",
            "pueden",
            "del",
            "las",
            "los",
            "una",
            "uno",
            "unos",
            "unas",
            "que",
            "con",
            "por",
            "sin"
        }

        texto_normalizado = (
            self._normalizar_texto(
                texto
            )
            .lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace(";", " ")
            .replace("(", " ")
            .replace(")", " ")
        )

        return {
            palabra
            for palabra in texto_normalizado.split()
            if (
                len(palabra) >= 4
                and palabra not in palabras_excluidas
            )
        }

    def calcular_similitud(
        self,
        texto_a,
        texto_b
    ) -> float:

        palabras_a = (
            self._palabras_significativas(
                texto_a
            )
        )

        palabras_b = (
            self._palabras_significativas(
                texto_b
            )
        )

        if not palabras_a or not palabras_b:
            return 0.0

        interseccion = (
            palabras_a.intersection(
                palabras_b
            )
        )

        union = (
            palabras_a.union(
                palabras_b
            )
        )

        if not union:
            return 0.0

        return round(
            len(interseccion) / len(union),
            4
        )

    # ======================================================
    # CONTRASTAR HALLAZGOS
    # ======================================================

    def contrastar_hallazgos(
        self,
        hallazgos,
        umbral_similitud=0.45
    ) -> List[Dict[str, Any]]:

        resultados = []

        for indice, hallazgo_a in enumerate(
            hallazgos
        ):

            coincidencias = []

            for posicion, hallazgo_b in enumerate(
                hallazgos
            ):

                if indice == posicion:
                    continue

                if (
                    hallazgo_a.get("fuente")
                    == hallazgo_b.get("fuente")
                ):
                    continue

                similitud = (
                    self.calcular_similitud(
                        hallazgo_a.get(
                            "afirmacion",
                            ""
                        ),
                        hallazgo_b.get(
                            "afirmacion",
                            ""
                        )
                    )
                )

                if similitud >= umbral_similitud:

                    coincidencias.append({
                        "hallazgo":
                            hallazgo_b.get("id"),

                        "fuente":
                            hallazgo_b.get("fuente"),

                        "similitud":
                            similitud
                    })

            nuevo_hallazgo = dict(
                hallazgo_a
            )

            nuevo_hallazgo[
                "coincidencias"
            ] = coincidencias

            nuevo_hallazgo[
                "fuentes_coincidentes"
            ] = len(
                {
                    coincidencia.get("fuente")
                    for coincidencia in coincidencias
                }
            )

            if coincidencias:

                nuevo_hallazgo[
                    "verificado"
                ] = True

                nuevo_hallazgo[
                    "estado"
                ] = "respaldado_por_otras_fuentes"

            else:

                nuevo_hallazgo[
                    "verificado"
                ] = False

                nuevo_hallazgo[
                    "estado"
                ] = "sin_confirmacion_independiente"

            resultados.append(
                nuevo_hallazgo
            )

        return resultados

    # ======================================================
    # DETECTAR LIMITACIONES
    # ======================================================

    def detectar_limitaciones(
        self,
        fuentes,
        hallazgos
    ) -> Listlimitaciones = []

        if not fuentes:

            limitaciones.append(
                "No se proporcionaron fuentes para la investigación."
            )

            return limitaciones

        if len(fuentes) == 1:

            limitaciones.append(
                "La investigación depende de una sola fuente."
            )

        fuentes_sin_autor = sum(
            1
            for fuente in fuentes
            if not fuente.get("autor")
        )

        fuentes_sin_fecha = sum(
            1
            for fuente in fuentes
            if not fuente.get("fecha")
        )

        fuentes_sin_origen = sum(
            1
            for fuente in fuentes
            if not (
                fuente.get("origen")
                or fuente.get("url")
            )
        )

        fuentes_baja_confianza = sum(
            1
            for fuente in fuentes
            if fuente.get(
                "evaluacion",
                {}
            ).get(
                "nivel"
            ) in {
                "baja",
                "muy_baja"
            }
        )

        hallazgos_sin_confirmar = sum(
            1
            for hallazgo in hallazgos
            if not hallazgo.get(
                "verificado",
                False
            )
        )

        if fuentes_sin_autor:

            limitaciones.append(
                (
                    f"{fuentes_sin_autor} fuente(s) "
                    f"no identifican autor."
                )
            )

        if fuentes_sin_fecha:

            limitaciones.append(
                (
                    f"{fuentes_sin_fecha} fuente(s) "
                    f"no especifican fecha."
                )
            )

        if fuentes_sin_origen:

            limitaciones.append(
                (
                    f"{fuentes_sin_origen} fuente(s) "
                    f"no identifican su origen."
                )
            )

        if fuentes_baja_confianza:

            limitaciones.append(
                (
                    f"{fuentes_baja_confianza} fuente(s) "
                    f"presentan baja confiabilidad documental."
                )
            )

        if hallazgos_sin_confirmar:

            limitaciones.append(
                (
                    f"{hallazgos_sin_confirmar} hallazgo(s) "
                    f"no tienen confirmación independiente."
                )
            )

        return limitaciones

    # ======================================================
    # CALCULAR CONFIANZA GENERAL
    # ======================================================

    def calcular_confianza(
        self,
        fuentes,
        hallazgos
    ) -> Dict[str, Any]:

        if not fuentes:

            return {
                "puntaje": 0,
                "nivel": "muy_baja"
            }

        promedio_fuentes = sum(
            fuente.get(
                "evaluacion",
                {}
            ).get(
                "puntaje",
                0
            )
            for fuente in fuentes
        ) / len(fuentes)

        if hallazgos:

            hallazgos_verificados = sum(
                1
                for hallazgo in hallazgos
                if hallazgo.get(
                    "verificado",
                    False
                )
            )

            proporcion_verificada = (
                hallazgos_verificados
                / len(hallazgos)
            )

        else:

            proporcion_verificada = 0.0

        puntaje = round(
            (
                promedio_fuentes * 0.65
                + proporcion_verificada * 100 * 0.35
            ),
            2
        )

        if puntaje >= 85:
            nivel = "muy_alta"

        elif puntaje >= 70:
            nivel = "alta"

        elif puntaje >= 50:
            nivel = "media"

        elif puntaje >= 30:
            nivel = "baja"

        else:
            nivel = "muy_baja"

        return {
            "puntaje":
                puntaje,

            "nivel":
                nivel
        }

    # ======================================================
    # GENERAR SÍNTESIS
    # ======================================================

    def generar_sintesis(
        self,
        tema,
        hallazgos,
        limite=10
    ) -> Dict[str, Any]:

        respaldados = [
            hallazgo
            for hallazgo in hallazgos
            if hallazgo.get(
                "verificado",
                False
            )
        ]

        pendientes = [
            hallazgo
            for hallazgo in hallazgos
            if not hallazgo.get(
                "verificado",
                False
            )
        ]

        principales = sorted(
            hallazgos,
            key=lambda elemento: (
                elemento.get(
                    "verificado",
                    False
                ),
                elemento.get(
                    "puntaje_fuente",
                    0
                ),
                elemento.get(
                    "fuentes_coincidentes",
                    0
                )
            ),
            reverse=True
        )[:limite]

        return {
            "tema":
                self._normalizar_texto(
                    tema
                ),

            "principales_hallazgos":
                principales,

            "hallazgos_respaldados":
                len(respaldados),

            "hallazgos_pendientes":
                len(pendientes),

            "conclusion":
                self._crear_conclusion(
                    tema,
                    principales,
                    respaldados
                )
        }

    def _crear_conclusion(
        self,
        tema,
        principales,
        respaldados
    ) -> str:

        if not principales:

            return (
                "No existe evidencia suficiente para "
                "generar una conclusión."
            )

        if respaldados:

            return (
                f"La investigación sobre "
                f"'{self._normalizar_texto(tema)}' "
                f"contiene hallazgos respaldados por "
                f"más de una fuente. Las afirmaciones "
                f"deben conservar su trazabilidad y "
                f"revisarse junto con las limitaciones."
            )

        return (
            f"La investigación sobre "
            f"'{self._normalizar_texto(tema)}' "
            f"contiene información útil, pero todavía "
            f"no cuenta con confirmación independiente "
            f"suficiente."
        )

    # ======================================================
    # INVESTIGAR
    # ======================================================

    def investigar(
        self,
        tema,
        fuentes=None,
        objetivo=None,
        preguntas=None
    ) -> Dict[str, Any]:

        inicio = datetime.now()

        plan = self.generar_plan(
            tema=tema,
            objetivo=objetivo,
            preguntas=preguntas
        )

        fuentes_normalizadas = (
            self.normalizar_fuentes(
                fuentes
            )
        )

        hallazgos_iniciales = (
            self.extraer_hallazgos(
                fuentes_normalizadas
            )
        )

        hallazgos = (
            self.contrastar_hallazgos(
                hallazgos_iniciales
            )
        )

        limitaciones = (
            self.detectar_limitaciones(
                fuentes_normalizadas,
                hallazgos
            )
        )

        confianza = (
            self.calcular_confianza(
                fuentes_normalizadas,
                hallazgos
            )
        )

        sintesis = (
            self.generar_sintesis(
                tema,
                hallazgos
            )
        )

        estado = (
            "completada"
            if fuentes_normalizadas
            else "sin_fuentes"
        )

        resultado = {
            "tipo":
                "investigacion",

            "tema":
                self._normalizar_texto(
                    tema
                ),

            "objetivo":
                plan.get("objetivo"),

            "fecha_inicio":
                inicio.isoformat(),

            "fecha_finalizacion":
                datetime.now().isoformat(),

            "estado":
                estado,

            "plan":
                plan,

            "fuentes":
                fuentes_normalizadas,

            "hallazgos":
                hallazgos,

            "sintesis":
                sintesis,

            "confianza":
                confianza,

            "limitaciones":
                limitaciones,

            "metricas": {
                "total_fuentes":
                    len(fuentes_normalizadas),

                "total_hallazgos":
                    len(hallazgos),

                "hallazgos_verificados":
                    sum(
                        1
                        for hallazgo in hallazgos
                        if hallazgo.get(
                            "verificado",
                            False
                        )
                    ),

                "hallazgos_pendientes":
                    sum(
                        1
                        for hallazgo in hallazgos
                        if not hallazgo.get(
                            "verificado",
                            False
                        )
                    )
            }
        }

        self._registrar_investigacion(
            resultado
        )

        return resultado

    # ======================================================
    # REGISTRAR INVESTIGACIÓN
    # ======================================================

    def _registrar_investigacion(
        self,
        investigacion
    ):

        self.total_investigaciones += 1

        metricas = investigacion.get(
            "metricas",
            {}
        )

        self.total_fuentes_procesadas += (
            metricas.get(
                "total_fuentes",
                0
            )
        )

        self.total_hallazgos += (
            metricas.get(
                "total_hallazgos",
                0
            )
        )

        resumen = {
            "tema":
                investigacion.get(
                    "tema"
                ),

            "fecha":
                investigacion.get(
                    "fecha_finalizacion"
                ),

            "estado":
                investigacion.get(
                    "estado"
                ),

            "confianza":
                investigacion.get(
                    "confianza"
                ),

            "metricas":
                metricas
        }

        self.ultima_investigacion = (
            resumen
        )

        self.historial.append(
            resumen
        )

        if len(self.historial) > 100:

            self.historial = (
                self.historial[-100:]
            )

    # ======================================================
    # RESOLVER
    # ======================================================

    def resolver(
        self,
        tarea,
        contexto
    ):

        if contexto is None:

            contexto = {}

        tema = contexto.get(
            "tema",
            tarea
        )

        fuentes = contexto.get(
            "fuentes",
            contexto.get(
                "documentos",
                contexto.get(
                    "contenido",
                    []
                )
            )
        )

        objetivo = contexto.get(
            "objetivo"
        )

        preguntas = contexto.get(
            "preguntas"
        )

        investigacion = self.investigar(
            tema=tema,
            fuentes=fuentes,
            objetivo=objetivo,
            preguntas=preguntas
        )

        if investigacion["estado"] == "sin_fuentes":

            estado = (
                "requiere_fuentes"
            )

            mensaje = (
                "La investigación fue preparada, "
                "pero requiere fuentes para generar "
                "hallazgos verificables."
            )

        elif (
            investigacion.get(
                "confianza",
                {}
            ).get(
                "nivel"
            ) in {
                "muy_baja",
                "baja"
            }
        ):

            estado = (
                "requiere_revision"
            )

            mensaje = (
                "La investigación fue completada, "
                "pero la evidencia disponible tiene "
                "un nivel de confianza limitado."
            )

        else:

            estado = (
                "completada"
            )

            mensaje = (
                "Investigación completada con "
                "trazabilidad de fuentes y hallazgos."
            )

        return {
            "agente":
                self.INTENT_TAG,

            "rol":
                self.ROLE,

            "nivel":
                self.AGENT_LEVEL,

            "version":
                self.VERSION,

            "estado":
                estado,

            "tarea":
                tarea,

            "investigacion":
                investigacion,

            "resultado":
                mensaje,

            "contexto":
                contexto
        }

    # ======================================================
    # ESTADÍSTICAS
    # ======================================================

    def estadisticas(
        self
    ) -> Dict[str, Any]:

        promedio_fuentes = 0.0

        promedio_hallazgos = 0.0

        if self.total_investigaciones > 0:

            promedio_fuentes = round(
                (
                    self.total_fuentes_procesadas
                    / self.total_investigaciones
                ),
                2
            )

            promedio_hallazgos = round(
                (
                    self.total_hallazgos
                    / self.total_investigaciones
                ),
                2
            )

        return {
            "total_investigaciones":
                self.total_investigaciones,

            "total_fuentes_procesadas":
                self.total_fuentes_procesadas,

            "total_hallazgos":
                self.total_hallazgos,

            "promedio_fuentes":
                promedio_fuentes,

            "promedio_hallazgos":
                promedio_hallazgos,

            "ultima_investigacion":
                self.ultima_investigacion
        }

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        datos = super().resumen()

        datos["tipo"] = (
            "investigacion_y_evidencia"
        )

        datos["version"] = (
            self.VERSION
        )

        datos["nivel"] = (
            self.AGENT_LEVEL
        )

        datos["especialidades"] = (
            list(
                self.SPECIALTIES
            )
        )

        datos["estadisticas"] = (
            self.estadisticas()
        )

        return datos


# ==========================================================
# COMPATIBILIDAD
# ==========================================================

ResearchAgent = AgenteInvestigador
AgenteInvestigacion = AgenteInvestigador
Investigador = AgenteInvestigador
