# ==========================================================
# DRAYMSYSTEM IA
# PROCESAMIENTO DE LENGUAJE NATURAL
# ==========================================================

import re
import unicodedata
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple


class MotorNLP:
    """
    Procesamiento de lenguaje natural básico de DraymSystem IA.

    Responsabilidades:
    - Limpiar y normalizar texto.
    - Tokenizar palabras.
    - Dividir texto en oraciones.
    - Extraer palabras clave.
    - Extraer frases repetidas.
    - Detectar intenciones configurables.
    - Calcular similitud léxica.
    - Identificar contenido relacionado con programación.
    - Preparar entradas para otros módulos.

    Este módulo no genera respuestas, no selecciona agentes
    y no ejecuta tareas.
    """

    VERSION = "1.0"

    PALABRAS_VACIAS: Set[str] = {
        "a", "al", "algo", "algunas", "algunos",
        "ante", "antes", "como", "con", "contra",
        "cual", "cuando", "de", "del", "desde",
        "donde", "durante", "e", "el", "ella",
        "ellas", "ellos", "en", "entre", "era",
        "es", "esa", "ese", "eso", "esta",
        "este", "esto", "fue", "ha", "hasta",
        "hay", "la", "las", "le", "les", "lo",
        "los", "mas", "me", "mi", "mis", "muy",
        "ni", "no", "nos", "o", "para", "pero",
        "por", "porque", "que", "se", "sin",
        "sobre", "su", "sus", "te", "tiene",
        "todo", "tu", "tus", "un", "una", "uno",
        "unos", "unas", "y", "ya", "yo"
    }

    PALABRAS_CODIGO: Set[str] = {
        "api",
        "backend",
        "bug",
        "clase",
        "codigo",
        "compilar",
        "depurar",
        "error",
        "frontend",
        "funcion",
        "html",
        "java",
        "javascript",
        "kernel",
        "metodo",
        "modulo",
        "programa",
        "programar",
        "python",
        "script",
        "software",
        "sql",
        "variable"
    }

    ACCIONES_CONOCIDAS: Set[str] = {
        "analiza",
        "analizar",
        "audita",
        "auditar",
        "busca",
        "buscar",
        "calcula",
        "calcular",
        "compara",
        "comparar",
        "construye",
        "construir",
        "crea",
        "crear",
        "desarrolla",
        "desarrollar",
        "disena",
        "disenar",
        "ejecuta",
        "ejecutar",
        "elimina",
        "eliminar",
        "escribe",
        "escribir",
        "explica",
        "explicar",
        "genera",
        "generar",
        "integra",
        "integrar",
        "investiga",
        "investigar",
        "modifica",
        "modificar",
        "organiza",
        "organizar",
        "planifica",
        "planificar",
        "programa",
        "programar",
        "revisa",
        "revisar",
        "resume",
        "resumir"
    }

    PATRONES_CODIGO = (
        re.compile(r"```[\s\S]*?```"),
        re.compile(r"\bdef\s+[a-zA-Z_]\w*\s*\("),
        re.compile(r"\bclass\s+[a-zA-Z_]\w*"),
        re.compile(r"\bimport\s+[a-zA-Z_]\w*"),
        re.compile(
            r"\bfrom\s+[a-zA-Z_]\w*\s+import\b"
        ),
        re.compile(
            r"\bfunction\s+[a-zA-Z_]\w*\s*\("
        ),
        re.compile(
            r"[a-zA-Z_]\w*\s*=\s*[^=]"
        ),
        re.compile(r"[{};]")
    )

    def __init__(
        self,
        intenciones: Optional[
            Dict[str, List[str]]
        ] = None,
        palabras_vacias: Optional[
            List[str]
        ] = None
    ):
        self.intenciones: Dict[
            str,
            List[str]
        ] = {}

        if palabras_vacias:

            self.palabras_vacias = {
                self.normalizar_texto(palabra)
                for palabra in palabras_vacias
                if palabra
            }

        else:

            self.palabras_vacias = set(
                self.PALABRAS_VACIAS
            )

        if intenciones:

            for nombre, patrones in intenciones.items():

                self.registrar_intencion(
                    nombre,
                    patrones
                )

    # ======================================================
    # VALIDAR TEXTO
    # ======================================================

    @staticmethod
    def _validar_texto(
        texto: Any
    ) -> str:

        if texto is None:
            return ""

        if isinstance(texto, str):
            return texto

        return str(texto)

    # ======================================================
    # QUITAR ACENTOS
    # ======================================================

    @staticmethod
    def quitar_acentos(
        texto: Any
    ) -> str:

        texto = MotorNLP._validar_texto(
            texto
        )

        texto_descompuesto = unicodedata.normalize(
            "NFD",
            texto
        )

        return "".join(
            caracter
            for caracter in texto_descompuesto
            if unicodedata.category(
                caracter
            ) != "Mn"
        )

    # ======================================================
    # NORMALIZAR TEXTO
    # ======================================================

    @classmethod
    def normalizar_texto(
        cls,
        texto: Any,
        conservar_puntuacion: bool = False
    ) -> str:

        texto = cls._validar_texto(
            texto
        ).lower()

        texto = cls.quitar_acentos(
            texto
        )

        texto = texto.replace(
            "\n",
            " "
        ).replace(
            "\t",
            " "
        )

        if conservar_puntuacion:

            texto = re.sub(
                (
                    r'''[^a-z0-9\s.,;:!?(){}'''
                    r'''$$$$_+\-*/=<>#'"\\]'''
                ),
                " ",
                texto
            )

        else:

            texto = re.sub(
                r"[^a-z0-9_\s+\-*/=<>#]",
                " ",
                texto
            )

        texto = re.sub(
            r"\s+",
            " ",
            texto
        )

        return texto.strip()

    # ======================================================
    # LIMPIAR TEXTO
    # ======================================================

    @staticmethod
    def limpiar_texto(
        texto: Any
    ) -> str:

        texto = MotorNLP._validar_texto(
            texto
        )

        texto = unicodedata.normalize(
            "NFC",
            texto
        )

        texto = re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F]",
            "",
            texto
        )

        texto = re.sub(
            r"[ \t]+",
            " ",
            texto
        )

        texto = re.sub(
            r"\n{3,}",
            "\n\n",
            texto
        )

        return texto.strip()

    # ======================================================
    # TOKENIZAR
    # ======================================================

    def tokenizar(
        self,
        texto: Any,
        eliminar_vacias: bool = False
    ) -> List:

        texto_normalizado = self.normalizar_texto(
            texto
        )

        tokens = re.findall(
            (
                r"[a-z0-9_+#]+"
                r"(?:[-*/=<>][a-z0-9_+#]+)*"
            ),
            texto_normalizado
        )

        if eliminar_vacias:

            tokens = [
                token
                for token in tokens
                if token not in self.palabras_vacias
            ]

        return tokens

    # ======================================================
    # DIVIDIR ORACIONES
    # ======================================================

    @staticmethod
    def dividir_oraciones(
        texto: Any
    ) -> List[str]:

        texto = MotorNLP.limpiar_texto(
            texto
        )

        if not texto:
            return []

        fragmentos = re.split(
            r"(?<=[.!?])\s+|\n+",
            texto
        )

        return [
            fragmento.strip()
            for fragmento in fragmentos
            if fragmento.strip()
        ]

    # ======================================================
    # CONTAR PALABRAS
    # ======================================================

    def contar_palabras(
        self,
        texto: Any
    ) -> Dict[str, int]:

        tokens = self.tokenizar(
            texto,
            eliminar_vacias=True
        )

        return dict(
            Counter(tokens)
        )

    # ======================================================
    # EXTRAER PALABRAS CLAVE
    # ======================================================

    def extraer_palabras_clave(
        self,
        texto: Any,
        limite: int = 10,
        longitud_minima: int = 3
    ) -> List[Dict[str, Any]]:

        limite = max(
            1,
            int(limite)
        )

        longitud_minima = max(
            1,
            int(longitud_minima)
        )

        tokens = self.tokenizar(
            texto,
            eliminar_vacias=True
        )

        tokens_validos = [
            token
            for token in tokens
            if (
                len(token) >= longitud_minima
                and not token.isdigit()
            )
        ]

        frecuencias = Counter(
            tokens_validos
        )

        total = sum(
            frecuencias.values()
        )

        if total == 0:
            return []

        palabras_ordenadas = sorted(
            frecuencias.items(),
            key=lambda elemento: (
                elemento[1],
                len(elemento[0])
            ),
            reverse=True
        )

        return [
            {
                "palabra": palabra,
                "frecuencia": frecuencia,
                "relevancia": round(
                    frecuencia / total,
                    4
                )
            }
            for palabra, frecuencia
            in palabras_ordenadas[:limite]
        ]

    # ======================================================
    # EXTRAER FRASES REPETIDAS
    # ======================================================

    def extraer_frases(
        self,
        texto: Any,
        longitud: int = 2,
        limite: int = 10
    ) -> List[Dict[str, Any]]:

        longitud = max(
            2,
            int(longitud)
        )

        limite = max(
            1,
            int(limite)
        )

        tokens = self.tokenizar(
            texto,
            eliminar_vacias=True
        )

        if len(tokens) < longitud:
            return []

        frases = [
            " ".join(
                tokens[indice:indice + longitud]
            )
            for indice in range(
                len(tokens) - longitud + 1
            )
        ]

        frecuencias = Counter(
            frases
        )

        frases_repetidas = [
            {
                "frase": frase,
                "frecuencia": frecuencia
            }
            for frase, frecuencia
            in frecuencias.most_common()
            if frecuencia > 1
        ]

        return frases_repetidas[:limite]

    # ======================================================
    # REGISTRAR INTENCIÓN
    # ======================================================

    def registrar_intencion(
        self,
        nombre: str,
        patrones: List[str]
    ) -> None:

        nombre_limpio = self.normalizar_texto(
            nombre
        ).replace(
            " ",
            "_"
        )

        if not nombre_limpio:

            raise ValueError(
                "La intención necesita un nombre."
            )

        if isinstance(patrones, str):
            patrones = [patrones]

        patrones_limpios = []

        for patron in patrones:

            patron_limpio = self.normalizar_texto(
                patron
            )

            if patron_limpio:

                patrones_limpios.append(
                    patron_limpio
                )

        if not patrones_limpios:

            raise ValueError(
                "La intención necesita al menos un patrón."
            )

        self.intenciones[
            nombre_limpio
        ] = patrones_limpios

    # ======================================================
    # ELIMINAR INTENCIÓN
    # ======================================================

    def eliminar_intencion(
        self,
        nombre: str
    ) -> bool:

        nombre_limpio = self.normalizar_texto(
            nombre
        ).replace(
            " ",
            "_"
        )

        if nombre_limpio not in self.intenciones:
            return False

        del self.intenciones[
            nombre_limpio
        ]

        return True

    # ======================================================
    # CALCULAR SIMILITUD
    # ======================================================

    def calcular_similitud(
        self,
        texto_a: Any,
        texto_b: Any
    ) -> float:

        tokens_a = set(
            self.tokenizar(
                texto_a,
                eliminar_vacias=True
            )
        )

        tokens_b = set(
            self.tokenizar(
                texto_b,
                eliminar_vacias=True
            )
        )

        if not tokens_a or not tokens_b:
            return 0.0

        interseccion = tokens_a.intersection(
            tokens_b
        )

        union = tokens_a.union(
            tokens_b
        )

        return round(
            len(interseccion) / len(union),
            4
        )

    # ======================================================
    # DETECTAR INTENCIÓN
    # ======================================================

    def detectar_intencion(
        self,
        texto: Any
    ) -> Dict[str, Any]:

        texto_normalizado = self.normalizar_texto(
            texto
        )

        respuesta_vacia = {
            "intencion": "desconocida",
            "confianza": 0.0,
            "patron": None,
            "alternativas": []
        }

        if not texto_normalizado:
            return respuesta_vacia

        evaluaciones = []

        for nombre, patrones in self.intenciones.items():

            mejor_confianza = 0.0
            mejor_patron = None

            for patron in patrones:

                if patron in texto_normalizado:

                    confianza = 1.0

                else:

                    confianza = self.calcular_similitud(
                        texto_normalizado,
                        patron
                    )

                if confianza > mejor_confianza:

                    mejor_confianza = confianza
                    mejor_patron = patron

            evaluaciones.append(
                {
                    "intencion": nombre,
                    "confianza": round(
                        mejor_confianza,
                        4
                    ),
                    "patron": mejor_patron
                }
            )

        evaluaciones.sort(
            key=lambda elemento: elemento[
                "confianza"
            ],
            reverse=True
        )

        if not evaluaciones:
            return respuesta_vacia

        mejor = evaluaciones[0]

        if mejor["confianza"] <= 0:

            respuesta_vacia[
                "alternativas"
            ] = evaluaciones[:3]

            return respuesta_vacia

        return {
            "intencion": mejor["intencion"],
            "confianza": mejor["confianza"],
            "patron": mejor["patron"],
            "alternativas": evaluaciones[1:4]
        }

    # ======================================================
    # DETECTAR CÓDIGO
    # ======================================================

    def detectar_codigo(
        self,
        texto: Any
    ) -> Dict[str, Any]:

        texto_original = self._validar_texto(
            texto
        )

        tokens = set(
            self.tokenizar(
                texto_original,
                eliminar_vacias=True
            )
        )

        palabras_encontradas = sorted(
            tokens.intersection(
                self.PALABRAS_CODIGO
            )
        )

        patrones_encontrados = [
            patron.pattern
            for patron in self.PATRONES_CODIGO
            if patron.search(
                texto_original
            )
        ]

        puntuacion = (
            len(palabras_encontradas)
            + len(patrones_encontrados) * 2
        )

        return {
            "contiene_codigo": puntuacion >= 2,
            "puntuacion": puntuacion,
            "palabras_detectadas":
                palabras_encontradas,
            "patrones_detectados":
                patrones_encontrados
        }

    # ======================================================
    # EXTRAER ACCIONES
    # ======================================================

    def extraer_acciones(
        self,
        texto: Any
    ) -> List:

        acciones = []
        acciones_vistas = set()

        for token in self.tokenizar(
            texto
        ):

            if (
                token in self.ACCIONES_CONOCIDAS
                and token not in acciones_vistas
            ):

                acciones.append(
                    token
                )

                acciones_vistas.add(
                    token
                )

        return acciones

    # ======================================================
    # ANALIZAR TEXTO
    # ======================================================

    def analizar(
        self,
        texto: Any,
        limite_palabras_clave: int = 10
    ) -> Dict[str, Any]:

        texto_original = self._validar_texto(
            texto
        )

        texto_limpio = self.limpiar_texto(
            texto_original
        )

        tokens = self.tokenizar(
            texto_limpio
        )

        oraciones = self.dividir_oraciones(
            texto_limpio
        )

        return {
            "version": self.VERSION,
            "texto_original": texto_original,
            "texto_limpio": texto_limpio,
            "texto_normalizado":
                self.normalizar_texto(
                    texto_limpio
                ),
            "tokens": tokens,
            "cantidad_tokens": len(tokens),
            "cantidad_oraciones":
                len(oraciones),
            "oraciones": oraciones,
            "palabras_clave":
                self.extraer_palabras_clave(
                    texto_limpio,
                    limite=limite_palabras_clave
                ),
            "acciones":
                self.extraer_acciones(
                    texto_limpio
                ),
            "intencion":
                self.detectar_intencion(
                    texto_limpio
                ),
            "codigo":
                self.detectar_codigo(
                    texto_original
                )
        }

    # ======================================================
    # ANALIZAR Y GUARDAR EN WORKSPACE
    # ======================================================

    def analizar_y_guardar(
        self,
        texto: Any,
        workspace: Any,
        clave: str = "ultimo_analisis_nlp"
    ) -> Dict[str, Any]:

        analisis = self.analizar(
            texto
        )

        workspace.guardar(
            clave,
            analisis
        )

        try:

            workspace.guardar_disco()

        except (
            AttributeError,
            OSError,
            TypeError
        ):

            pass

        return analisis

    # ======================================================
    # PREPARAR ENTRADA
    # ======================================================

    def preparar_entrada(
        self,
        texto: Any
    ) -> Tuple[str, List[str]]:

        texto_limpio = self.limpiar_texto(
            texto
        )

        tokens = self.tokenizar(
            texto_limpio
        )

        return texto_limpio, tokens


# Nombres alternativos compatibles
NLP = MotorNLP
ProcesadorLenguaje = MotorNLP
