# ==========================================================
# DRAYMSYSTEM IA
# AGENTE QA
# ASEGURAMIENTO DE CALIDAD
# ==========================================================

import ast

from datetime import datetime
from typing import Any, Dict, List, Optional

from agentes.agente_general import AgenteGeneral


class AgenteQA(AgenteGeneral):

    INTENT_TAG = "qa"

    AGENT_LEVEL = 4

    ROLE = "quality_assurance"

    VERSION = "2.0.0"

    SPECIALTIES = [
        "qa",
        "testing",
        "calidad",
        "validacion",
        "revision",
        "errores",
        "auditoria",
        "verificacion",
        "integridad",
        "analisis_codigo",
        "consistencia",
        "seguridad"
    ]

    PALABRAS_CLAVE = {
        "qa",
        "test",
        "testing",
        "prueba",
        "pruebas",
        "error",
        "errores",
        "fallo",
        "fallos",
        "validar",
        "validacion",
        "revision",
        "auditoria",
        "control",
        "calidad",
        "verificar",
        "integridad",
        "codigo",
        "depurar"
    }

    # Penalización aplicada al puntaje por gravedad.
    PENALIZACIONES = {
        "informativa": 2,
        "baja": 5,
        "media": 10,
        "alta": 20,
        "critica": 35
    }

    # Límites utilizados durante el análisis de código.
    MAX_LINEAS_FUNCION = 50
    MAX_ARGUMENTOS_FUNCION = 7
    MAX_COMPLEJIDAD = 10

    def __init__(self):

        super().__init__()

        self.fecha_creacion = (
            datetime.now()
        )

        self.total_auditorias = 0

        self.total_aprobadas = 0

        self.total_rechazadas = 0

        self.ultima_auditoria = None

    # ======================================================
    # UTILIDADES INTERNAS
    # ======================================================

    def _crear_problema(
        self,
        codigo: str,
        mensaje: str,
        gravedad: str = "media",
        categoria: str = "general",
        linea: Optional[int] = None
    ) -> Dict[str, Any]:

        problema = {
            "codigo":
                codigo,

            "mensaje":
                mensaje,

            "gravedad":
                gravedad,

            "categoria":
                categoria
        }

        if linea is not None:

            problema["linea"] = (
                linea
            )

        return problema

    def _eliminar_duplicados(
        self,
        elementos: List[Any]
    ) -> List:

        resultado = []

        claves_vistas = set()

        for elemento in elementos:

            if isinstance(
                elemento,
                dict
            ):

                clave = (
                    elemento.get("codigo"),
                    elemento.get("mensaje"),
                    elemento.get("linea")
                )

            else:

                clave = str(
                    elemento
                )

            if clave not in claves_vistas:

                claves_vistas.add(
                    clave
                )

                resultado.append(
                    elemento
                )

        return resultado

    def _normalizar_texto(
        self,
        contenido
    ) -> str:

        if contenido is None:
            return ""

        return str(
            contenido
        ).strip()

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

        return any(
            palabra in texto
            for palabra in self.PALABRAS_CLAVE
        )

    # ======================================================
    # DETECTAR PROBLEMAS GENERALES
    # ======================================================

    def detectar_problemas(
        self,
        contenido
    ) -> List[Dict[str, Any]]:

        problemas = []

        if contenido is None:

            problemas.append(
                self._crear_problema(
                    codigo="CONTENIDO_NULO",
                    mensaje="Resultado vacío.",
                    gravedad="critica",
                    categoria="integridad"
                )
            )

            return problemas

        texto = self._normalizar_texto(
            contenido
        )

        if not texto:

            problemas.append(
                self._crear_problema(
                    codigo="CONTENIDO_VACIO",
                    mensaje="Contenido vacío.",
                    gravedad="critica",
                    categoria="integridad"
                )
            )

            return problemas

        if len(texto) < 10:

            problemas.append(
                self._crear_problema(
                    codigo="CONTENIDO_CORTO",
                    mensaje="Contenido demasiado corto.",
                    gravedad="media",
                    categoria="contenido"
                )
            )

        if len(texto) > 50000:

            problemas.append(
                self._crear_problema(
                    codigo="CONTENIDO_EXTENSO",
                    mensaje=(
                        "El contenido es demasiado extenso "
                        "para una validación básica."
                    ),
                    gravedad="baja",
                    categoria="contenido"
                )
            )

        texto_mayusculas = texto.upper()

        marcadores = {
            "TODO": (
                "TAREA_PENDIENTE",
                "Contiene tareas pendientes.",
                "media"
            ),

            "FIXME": (
                "CORRECCION_PENDIENTE",
                "Contiene correcciones pendientes.",
                "alta"
            ),

            "HACK": (
                "SOLUCION_TEMPORAL",
                "Contiene una solución temporal marcada como HACK.",
                "media"
            ),

            "XXX": (
                "REVISION_PENDIENTE",
                "Contiene una sección marcada para revisión.",
                "media"
            )
        }

        for marcador, datos in marcadores.items():

            if marcador in texto_mayusculas:

                codigo, mensaje, gravedad = (
                    datos
                )

                problemas.append(
                    self._crear_problema(
                        codigo=codigo,
                        mensaje=mensaje,
                        gravedad=gravedad,
                        categoria="pendientes"
                    )
                )

        indicadores_error = [
            "TRACEBACK",
            "EXCEPTION",
            "FATAL ERROR",
            "CRITICAL ERROR",
            "ERROR:"
        ]

        if any(
            indicador in texto_mayusculas
            for indicador in indicadores_error
        ):

            problemas.append(
                self._crear_problema(
                    codigo="ERROR_REPORTADO",
                    mensaje="Posible error reportado en el contenido.",
                    gravedad="alta",
                    categoria="errores"
                )
            )

        return self._eliminar_duplicados(
            problemas
        )

    # ======================================================
    # PUNTUACIÓN DE CALIDAD
    # ======================================================

    def calcular_puntaje(
        self,
        problemas
    ) -> int:

        puntaje = 100

        for problema in problemas:

            gravedad = problema.get(
                "gravedad",
                "media"
            )

            penalizacion = (
                self.PENALIZACIONES.get(
                    gravedad,
                    10
                )
            )

            puntaje -= penalizacion

        return max(
            0,
            min(
                100,
                puntaje
            )
        )

    def evaluar_calidad(
        self,
        contenido=None,
        problemas=None
    ) -> str:

        if problemas is None:

            problemas = self.detectar_problemas(
                contenido
            )

        puntaje = self.calcular_puntaje(
            problemas
        )

        if puntaje >= 90:
            return "excelente"

        if puntaje >= 75:
            return "aceptable"

        if puntaje >= 50:
            return "deficiente"

        return "critica"

    # ======================================================
    # GENERAR RECOMENDACIONES
    # ======================================================

    def generar_recomendaciones(
        self,
        problemas
    ) -> List:

        recomendaciones = []

        mapa_recomendaciones = {
            "CONTENIDO_NULO":
                "Generar un resultado antes de ejecutar la auditoría.",

            "CONTENIDO_VACIO":
                "Completar la información faltante.",

            "CONTENIDO_CORTO":
                "Agregar más detalles y contexto al resultado.",

            "CONTENIDO_EXTENSO":
                "Dividir el contenido en secciones más pequeñas.",

            "TAREA_PENDIENTE":
                "Resolver las tareas marcadas como TODO.",

            "CORRECCION_PENDIENTE":
                "Corregir los elementos marcados como FIXME.",

            "SOLUCION_TEMPORAL":
                "Reemplazar las soluciones temporales por una implementación definitiva.",

            "REVISION_PENDIENTE":
                "Revisar las secciones marcadas antes de aprobar el resultado.",

            "ERROR_REPORTADO":
                "Revisar el error reportado y validar su causa.",

            "SINTAXIS_INVALIDA":
                "Corregir la sintaxis antes de ejecutar el código.",

            "PRINT_DEPURACION":
                "Eliminar o reemplazar las impresiones de depuración por un sistema de logging.",

            "PASS_DETECTADO":
                "Completar los bloques que sólo contienen pass.",

            "EXCEPCION_GENERICA":
                "Capturar excepciones específicas en lugar de usar except genérico.",

            "FUNCION_COMPLEJA":
                "Dividir la función en unidades más pequeñas y específicas.",

            "FUNCION_EXTENSA":
                "Reducir el tamaño de la función mediante métodos auxiliares.",

            "DEMASIADOS_ARGUMENTOS":
                "Reducir los argumentos o agruparlos en una estructura de configuración.",

            "SIN_DOCSTRING":
                "Agregar documentación a clases y funciones públicas.",

            "IMPORT_DUPLICADO":
                "Eliminar imports duplicados.",

            "IMPORT_NO_USADO":
                "Eliminar imports que no se utilizan.",

            "COMPARACION_NONE":
                "Usar 'is None' o 'is not None' para comparar con None.",

            "BARE_RAISE":
                "Especificar claramente la excepción que debe generarse.",

            "CODIGO_VACIO":
                "Agregar código válido antes de ejecutar la revisión."
        }

        for problema in problemas:

            codigo = problema.get(
                "codigo"
            )

            recomendacion = (
                mapa_recomendaciones.get(
                    codigo
                )
            )

            if recomendacion:

                recomendaciones.append(
                    recomendacion
                )

        return list(
            dict.fromkeys(
                recomendaciones
            )
        )

    # ======================================================
    # MÉTRICAS DE PROBLEMAS
    # ======================================================

    def generar_metricas(
        self,
        problemas
    ) -> Dict[str, Any]:

        por_gravedad = {
            "informativa": 0,
            "baja": 0,
            "media": 0,
            "alta": 0,
            "critica": 0
        }

        por_categoria = {}

        for problema in problemas:

            gravedad = problema.get(
                "gravedad",
                "media"
            )

            categoria = problema.get(
                "categoria",
                "general"
            )

            por_gravedad[gravedad] = (
                por_gravedad.get(
                    gravedad,
                    0
                ) + 1
            )

            por_categoria[categoria] = (
                por_categoria.get(
                    categoria,
                    0
                ) + 1
            )

        return {
            "total_problemas":
                len(problemas),

            "por_gravedad":
                por_gravedad,

            "por_categoria":
                por_categoria
        }

    # ======================================================
    # AUDITAR RESULTADO
    # ======================================================

    def auditar(
        self,
        resultado
    ) -> Dict[str, Any]:

        problemas = self.detectar_problemas(
            resultado
        )

        puntaje = self.calcular_puntaje(
            problemas
        )

        calidad = self.evaluar_calidad(
            problemas=problemas
        )

        recomendaciones = (
            self.generar_recomendaciones(
                problemas
            )
        )

        metricas = self.generar_metricas(
            problemas
        )

        aprobado = (
            puntaje >= 75
            and not any(
                problema.get("gravedad") == "critica"
                for problema in problemas
            )
        )

        auditoria = {
            "tipo":
                "contenido",

            "fecha":
                datetime.now().isoformat(),

            "puntaje":
                puntaje,

            "calidad":
                calidad,

            "problemas":
                problemas,

            "recomendaciones":
                recomendaciones,

            "metricas":
                metricas,

            "aprobado":
                aprobado
        }

        self._registrar_auditoria(
            auditoria
        )

        return auditoria

    # ======================================================
    # ANALIZADOR AST
    # ======================================================

    def _calcular_complejidad(
        self,
        nodo
    ) -> int:

        complejidad = 1

        tipos_decision = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.Try,
            ast.With,
            ast.AsyncWith,
            ast.IfExp,
            ast.comprehension,
            ast.Match
        )

        for elemento in ast.walk(
            nodo
        ):

            if isinstance(
                elemento,
                tipos_decision
            ):

                complejidad += 1

            elif isinstance(
                elemento,
                ast.BoolOp
            ):

                complejidad += max(
                    1,
                    len(elemento.values) - 1
                )

            elif isinstance(
                elemento,
                ast.ExceptHandler
            ):

                complejidad += 1

        return complejidad

    def _obtener_imports(
        self,
        arbol
    ):

        imports = []

        for nodo in ast.walk(
            arbol
        ):

            if isinstance(
                nodo,
                ast.Import
            ):

                for alias in nodo.names:

                    nombre_usado = (
                        alias.asname
                        or alias.name.split(".")[0]
                    )

                    imports.append({
                        "nombre":
                            alias.name,

                        "nombre_usado":
                            nombre_usado,

                        "linea":
                            getattr(
                                nodo,
                                "lineno",
                                None
                            )
                    })

            elif isinstance(
                nodo,
                ast.ImportFrom
            ):

                for alias in nodo.names:

                    if alias.name == "*":
                        continue

                    nombre_usado = (
                        alias.asname
                        or alias.name
                    )

                    imports.append({
                        "nombre":
                            alias.name,

                        "nombre_usado":
                            nombre_usado,

                        "linea":
                            getattr(
                                nodo,
                                "lineno",
                                None
                            )
                    })

        return imports

    def _obtener_nombres_usados(
        self,
        arbol
    ):

        return {
            nodo.id
            for nodo in ast.walk(arbol)
            if isinstance(
                nodo,
                ast.Name
            )
            and isinstance(
                nodo.ctx,
                ast.Load
            )
        }

    # ======================================================
    # REVISAR CÓDIGO
    # ======================================================

    def revisar_codigo(
        self,
        codigo
    ) -> List[Dict[str, Any]]:

        observaciones = []

        texto = self._normalizar_texto(
            codigo
        )

        if not texto:

            observaciones.append(
                self._crear_problema(
                    codigo="CODIGO_VACIO",
                    mensaje="Código vacío.",
                    gravedad="critica",
                    categoria="codigo"
                )
            )

            return observaciones

        try:

            arbol = ast.parse(
                texto
            )

        except SyntaxError as error:

            observaciones.append(
                self._crear_problema(
                    codigo="SINTAXIS_INVALIDA",
                    mensaje=(
                        error.msg
                        or "El código contiene sintaxis inválida."
                    ),
                    gravedad="critica",
                    categoria="sintaxis",
                    linea=error.lineno
                )
            )

            return observaciones

        imports = self._obtener_imports(
            arbol
        )

        nombres_usados = (
            self._obtener_nombres_usados(
                arbol
            )
        )

        imports_vistos = set()

        for importacion in imports:

            nombre = importacion[
                "nombre"
            ]

            nombre_usado = importacion[
                "nombre_usado"
            ]

            linea = importacion[
                "linea"
            ]

            if nombre in imports_vistos:

                observaciones.append(
                    self._crear_problema(
                        codigo="IMPORT_DUPLICADO",
                        mensaje=(
                            f"Import duplicado detectado: "
                            f"{nombre}."
                        ),
                        gravedad="baja",
                        categoria="imports",
                        linea=linea
                    )
                )

            imports_vistos.add(
                nombre
            )

            if nombre_usado not in nombres_usados:

                observaciones.append(
                    self._crear_problema(
                        codigo="IMPORT_NO_USADO",
                        mensaje=(
                            f"Import posiblemente no utilizado: "
                            f"{nombre}."
                        ),
                        gravedad="baja",
                        categoria="imports",
                        linea=linea
                    )
                )

        for nodo in ast.walk(
            arbol
        ):

            if isinstance(
                nodo,
                ast.Call
            ):

                if (
                    isinstance(
                        nodo.func,
                        ast.Name
                    )
                    and nodo.func.id == "print"
                ):

                    observaciones.append(
                        self._crear_problema(
                            codigo="PRINT_DEPURACION",
                            mensaje=(
                                "Posible impresión de "
                                "depuración detectada."
                            ),
                            gravedad="baja",
                            categoria="mantenimiento",
                            linea=getattr(
                                nodo,
                                "lineno",
                                None
                            )
                        )
                    )

            elif isinstance(
                nodo,
                ast.Pass
            ):

                observaciones.append(
                    self._crear_problema(
                        codigo="PASS_DETECTADO",
                        mensaje=(
                            "Bloque posiblemente "
                            "incompleto detectado."
                        ),
                        gravedad="media",
                        categoria="implementacion",
                        linea=getattr(
                            nodo,
                            "lineno",
                            None
                        )
                    )
                )

            elif isinstance(
                nodo,
                ast.ExceptHandler
            ):

                if nodo.type is None:

                    observaciones.append(
                        self._crear_problema(
                            codigo="EXCEPCION_GENERICA",
                            mensaje=(
                                "Captura genérica de "
                                "excepción detectada."
                            ),
                            gravedad="alta",
                            categoria="errores",
                            linea=getattr(
                                nodo,
                                "lineno",
                                None
                            )
                        )
                    )

            elif isinstance(
                nodo,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):

                self._revisar_funcion(
                    nodo,
                    observaciones
                )

            elif isinstance(
                nodo,
                ast.ClassDef
            ):

                if (
                    not nodo.name.startswith("_")
                    and ast.get_docstring(nodo) is None
                ):

                    observaciones.append(
                        self._crear_problema(
                            codigo="SIN_DOCSTRING",
                            mensaje=(
                                f"La clase pública "
                                f"'{nodo.name}' no tiene "
                                f"docstring."
                            ),
                            gravedad="informativa",
                            categoria="documentacion",
                            linea=getattr(
                                nodo,
                                "lineno",
                                None
                            )
                        )
                    )

            elif isinstance(
                nodo,
                ast.Compare
            ):

                valores = [
                    nodo.left,
                    *nodo.comparators
                ]

                contiene_none = any(
                    isinstance(
                        valor,
                        ast.Constant
                    )
                    and valor.value is None
                    for valor in valores
                )

                operadores_incorrectos = any(
                    isinstance(
                        operador,
                        (
                            ast.Eq,
                            ast.NotEq
                        )
                    )
                    for operador in nodo.ops
                )

                if (
                    contiene_none
                    and operadores_incorrectos
                ):

                    observaciones.append(
                        self._crear_problema(
                            codigo="COMPARACION_NONE",
                            mensaje=(
                                "Comparación con None "
                                "mediante == o !=."
                            ),
                            gravedad="baja",
                            categoria="estilo",
                            linea=getattr(
                                nodo,
                                "lineno",
                                None
                            )
                        )
                    )

        return self._eliminar_duplicados(
            observaciones
        )

    def _revisar_funcion(
        self,
        nodo,
        observaciones
    ):

        nombre = nodo.name

        linea_inicio = getattr(
            nodo,
            "lineno",
            0
        )

        linea_final = getattr(
            nodo,
            "end_lineno",
            linea_inicio
        )

        total_lineas = max(
            1,
            linea_final - linea_inicio + 1
        )

        argumentos = (
            len(nodo.args.posonlyargs)
            + len(nodo.args.args)
            + len(nodo.args.kwonlyargs)
        )

        if nodo.args.vararg is not None:
            argumentos += 1

        if nodo.args.kwarg is not None:
            argumentos += 1

        if (
            nodo.args.args
            and nodo.args.args[0].arg in {
                "self",
                "cls"
            }
        ):

            argumentos -= 1

        complejidad = (
            self._calcular_complejidad(
                nodo
            )
        )

        if total_lineas > self.MAX_LINEAS_FUNCION:

            observaciones.append(
                self._crear_problema(
                    codigo="FUNCION_EXTENSA",
                    mensaje=(
                        f"La función '{nombre}' tiene "
                        f"{total_lineas} líneas."
                    ),
                    gravedad="media",
                    categoria="complejidad",
                    linea=linea_inicio
                )
            )

        if argumentos > self.MAX_ARGUMENTOS_FUNCION:

            observaciones.append(
                self._crear_problema(
                    codigo="DEMASIADOS_ARGUMENTOS",
                    mensaje=(
                        f"La función '{nombre}' recibe "
                        f"{argumentos} argumentos."
                    ),
                    gravedad="media",
                    categoria="diseño",
                    linea=linea_inicio
                )
            )

        if complejidad > self.MAX_COMPLEJIDAD:

            observaciones.append(
                self._crear_problema(
                    codigo="FUNCION_COMPLEJA",
                    mensaje=(
                        f"La función '{nombre}' tiene una "
                        f"complejidad estimada de "
                        f"{complejidad}."
                    ),
                    gravedad="alta",
                    categoria="complejidad",
                    linea=linea_inicio
                )
            )

        if (
            not nombre.startswith("_")
            and ast.get_docstring(nodo) is None
        ):

            observaciones.append(
                self._crear_problema(
                    codigo="SIN_DOCSTRING",
                    mensaje=(
                        f"La función pública "
                        f"'{nombre}' no tiene docstring."
                    ),
                    gravedad="informativa",
                    categoria="documentacion",
                    linea=linea_inicio
                )
            )

    # ======================================================
    # AUDITAR CÓDIGO
    # ======================================================

    def auditar_codigo(
        self,
        codigo
    ) -> Dict[str, Any]:

        problemas_generales = (
            self.detectar_problemas(
                codigo
            )
        )

        problemas_codigo = (
            self.revisar_codigo(
                codigo
            )
        )

        problemas = (
            problemas_generales
            + problemas_codigo
        )

        problemas = self._eliminar_duplicados(
            problemas
        )

        puntaje = self.calcular_puntaje(
            problemas
        )

        calidad = self.evaluar_calidad(
            problemas=problemas
        )

        recomendaciones = (
            self.generar_recomendaciones(
                problemas
            )
        )

        metricas = self.generar_metricas(
            problemas
        )

        aprobado = (
            puntaje >= 75
            and not any(
                problema.get("gravedad")
                in {
                    "critica",
                    "alta"
                }
                for problema in problemas
            )
        )

        auditoria = {
            "tipo":
                "codigo",

            "fecha":
                datetime.now().isoformat(),

            "puntaje":
                puntaje,

            "calidad":
                calidad,

            "problemas":
                problemas,

            "recomendaciones":
                recomendaciones,

            "metricas":
                metricas,

            "aprobado":
                aprobado
        }

        self._registrar_auditoria(
            auditoria
        )

        return auditoria

    # ======================================================
    # REGISTRAR AUDITORÍA
    # ======================================================

    def _registrar_auditoria(
        self,
        auditoria
    ):

        self.total_auditorias += 1

        if auditoria.get(
            "aprobado",
            False
        ):

            self.total_aprobadas += 1

        else:

            self.total_rechazadas += 1

        self.ultima_auditoria = {
            "fecha":
                auditoria.get("fecha"),

            "tipo":
                auditoria.get("tipo"),

            "puntaje":
                auditoria.get("puntaje"),

            "calidad":
                auditoria.get("calidad"),

            "aprobado":
                auditoria.get("aprobado")
        }

    # ======================================================
    # DETECTAR TIPO DE AUDITORÍA
    # ======================================================

    def _es_codigo_python(
        self,
        contenido
    ) -> bool:

        texto = self._normalizar_texto(
            contenido
        )

        if not texto:
            return False

        indicadores = [
            "def ",
            "class ",
            "import ",
            "from ",
            "async def ",
            "if __name__"
        ]

        if not any(
            indicador in texto
            for indicador in indicadores
        ):

            return False

        try:

            ast.parse(
                texto
            )

            return True

        except SyntaxError:

            # Aunque sea inválido, puede seguir siendo código.
            return any(
                indicador in texto
                for indicador in indicadores
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

        contenido = contexto.get(
            "resultado",
            contexto.get(
                "codigo",
                tarea
            )
        )

        tipo_solicitado = str(
            contexto.get(
                "tipo_auditoria",
                ""
            )
        ).lower()

        es_codigo = (
            tipo_solicitado == "codigo"
            or "codigo" in contexto
            or self._es_codigo_python(
                contenido
            )
        )

        if es_codigo:

            auditoria = self.auditar_codigo(
                contenido
            )

        else:

            auditoria = self.auditar(
                contenido
            )

        if auditoria["aprobado"]:

            estado = "completada"

            resultado = (
                "Auditoría QA completada y aprobada."
            )

        else:

            estado = "requiere_revision"

            resultado = (
                "Auditoría QA completada con "
                "observaciones pendientes."
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

            "auditoria":
                auditoria,

            "resultado":
                resultado,

            "contexto":
                contexto
        }

    # ======================================================
    # ESTADÍSTICAS
    # ======================================================

    def estadisticas(
        self
    ) -> Dict[str, Any]:

        porcentaje_aprobacion = 0.0

        if self.total_auditorias > 0:

            porcentaje_aprobacion = round(
                (
                    self.total_aprobadas
                    / self.total_auditorias
                ) * 100,
                2
            )

        return {
            "total_auditorias":
                self.total_auditorias,

            "aprobadas":
                self.total_aprobadas,

            "rechazadas":
                self.total_rechazadas,

            "porcentaje_aprobacion":
                porcentaje_aprobacion,

            "ultima_auditoria":
                self.ultima_auditoria
        }

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        datos = super().resumen()

        datos["tipo"] = (
            "aseguramiento_calidad"
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

QualityAssurance = AgenteQA
AgenteCalidad = AgenteQA
