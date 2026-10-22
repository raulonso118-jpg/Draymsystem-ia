# ==========================================================
# DRAYMSYSTEM IA
# TOKENIZADOR PERSISTENTE CON SOPORTE PARA CODIGO
# ==========================================================

import json
import os
import re
import tempfile
import unicodedata

from collections import Counter

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Union
)


class TokenizadorDraym:
    """
    Tokenizador persistente de DraymSystem IA.

    Responsabilidades:
    - Preservar mayúsculas y minúsculas.
    - Separar palabras, números y símbolos.
    - Reconocer operadores de programación.
    - Construir vocabularios.
    - Convertir tokens a identificadores.
    - Convertir identificadores nuevamente a texto.
    - Procesar lotes de texto.
    - Guardar y recuperar el vocabulario.
    - Preparar entradas para futuros Transformers.
    """

    VERSION = "1.1"

    TOKENS_ESPECIALES = [
        "<PAD>",
        "<UNK>",
        "<BOS>",
        "<EOS>",
        "<CODE_START>",
        "<CODE_END>",
        "<NEWLINE>",
        "<TAB>",
        "<INDENT>",
        "<DEDENT>"
    ]

    def __init__(
        self,
        vocab_size: int = 5000,
        archivo_vocabulario: str = (
            "datos/tokenizador/vocabulario.json"
        ),
        minusculas: bool = False
    ):
        self.vocab_size = max(
            len(self.TOKENS_ESPECIALES),
            int(vocab_size)
        )

        self.archivo_vocabulario = (
            archivo_vocabulario
        )

        self.minusculas = bool(
            minusculas
        )

        self.vocabulario: List[str] = []

        self.token_a_id: Dict[str, int] = {}

        self.id_a_token: Dict[int, str] = {}

        self.frecuencias: Dict[str, int] = {}

        self._reiniciar_vocabulario()

        self.cargar()

    # ======================================================
    # REINICIAR VOCABULARIO
    # ======================================================

    def _reiniciar_vocabulario(
        self
    ) -> None:

        self.vocabulario = list(
            self.TOKENS_ESPECIALES
        )

        self.frecuencias = {
            token: 0
            for token in self.TOKENS_ESPECIALES
        }

        self._reconstruir_indices()

    # ======================================================
    # RECONSTRUIR INDICES
    # ======================================================

    def _reconstruir_indices(
        self
    ) -> None:

        self.token_a_id = {
            token: indice
            for indice, token
            in enumerate(self.vocabulario)
        }

        self.id_a_token = {
            indice: token
            for indice, token
            in enumerate(self.vocabulario)
        }

    # ======================================================
    # CONVERTIR A TEXTO
    # ======================================================

    @staticmethod
    def _a_texto(
        texto: Any
    ) -> str:

        if texto is None:
            return ""

        if isinstance(texto, str):
            return texto

        return str(texto)

    # ======================================================
    # NORMALIZAR
    # ======================================================

    def normalizar(
        self,
        texto: Any
    ) -> str:

        texto = unicodedata.normalize(
            "NFC",
            self._a_texto(texto)
        )

        if self.minusculas:
            texto = texto.lower()

        texto = texto.replace(
            "\r\n",
            "\n"
        ).replace(
            "\r",
            "\n"
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
    # PREPARAR CODIGO
    # ======================================================

    def preparar_codigo(
        self,
        codigo: Any,
        conservar_saltos: bool = True
    ) -> str:

        codigo = self._a_texto(
            codigo
        )

        codigo = unicodedata.normalize(
            "NFC",
            codigo
        )

        codigo = codigo.replace(
            "\r\n",
            "\n"
        ).replace(
            "\r",
            "\n"
        )

        if self.minusculas:
            codigo = codigo.lower()

        if conservar_saltos:

            codigo = codigo.replace(
                "\t",
                " <TAB> "
            )

            codigo = codigo.replace(
                "\n",
                " <NEWLINE> "
            )

        return codigo.strip()

    # ======================================================
    # DETECTAR POSIBLE CODIGO
    # ======================================================

    @staticmethod
    def parece_codigo(
        texto: Any
    ) -> bool:

        texto = TokenizadorDraym._a_texto(
            texto
        )

        indicadores = (
            r"```",
            r"\bdef\s+\w+\s*\(",
            r"\bclass\s+\w+",
            r"\bimport\s+\w+",
            r"\bfrom\s+\w+\s+import\b",
            r"\bfunction\s+\w+\s*\(",
            r"\breturn\b",
            r"\bif\s+.+:",
            r"\bfor\s+.+:",
            r"\bwhile\s+.+:",
            r"[{};]",
            r"==|!=|<=|>=|:=|->|=>"
        )

        return any(
            re.search(
                patron,
                texto
            )
            for patron in indicadores
        )

    # ======================================================
    # PRETOKENIZAR
    # ======================================================

    def pretokenizar(
        self,
        texto: Any,
        modo_codigo: Optional[bool] = None
    ) -> List[str]:

        if modo_codigo is None:

            modo_codigo = self.parece_codigo(
                texto
            )

        if modo_codigo:

            texto = self.preparar_codigo(
                texto,
                conservar_saltos=True
            )

        else:

            texto = self.normalizar(
                texto
            )

        if not texto:
            return []

        patron = (
            r"<CODE_START>"
            r"|<CODE_END>"
            r"|<NEWLINE>"
            r"|<TAB>"
            r"|<INDENT>"
            r"|<DEDENT>"
            r"|```"
            r"|=="
            r"|!="
            r"|<="
            r"|>="
            r"|:="
            r"|->"
            r"|=>"
            r"|\*\*"
            r"|//"
            r"|&&"
            r"|\|\|"
            r"|\+="
            r"|-="
            r"|\*="
            r"|/="
            r"|%="
            r"|<<"
            r"|>>"
            r"|[A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]"
            r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_]*"
            r"|\d+(?:\.\d+)?"
            r"|[^\w\s]"
        )

        tokens = re.findall(
            patron,
            texto,
            flags=re.UNICODE
        )

        if modo_codigo:

            tokens = [
                "<CODE_START>",
                *tokens,
                "<CODE_END>"
            ]

        return tokens

    # ======================================================
    # CONSTRUIR VOCABULARIO
    # ======================================================

    def construir_vocabulario(
        self,
        corpus: Iterable[Any],
        frecuencia_minima: int = 1,
        reiniciar: bool = True
    ) -> Dict[str, Any]:

        frecuencia_minima = max(
            1,
            int(frecuencia_minima)
        )

        if reiniciar:
            self._reiniciar_vocabulario()

        contador: Counter[str] = Counter()

        for texto in corpus:

            tokens = self.pretokenizar(
                texto
            )

            contador.update(
                tokens
            )

        espacios_disponibles = (
            self.vocab_size
            - len(self.vocabulario)
        )

        candidatos = sorted(
            (
                (token, frecuencia)
                for token, frecuencia
                in contador.items()
                if (
                    frecuencia >= frecuencia_minima
                    and token not in self.token_a_id
                )
            ),
            key=lambda elemento: (
                -elemento[1],
                elemento[0]
            )
        )

        for token, frecuencia in candidatos[
            :espacios_disponibles
        ]:

            self.vocabulario.append(
                token
            )

            self.frecuencias[
                token
            ] = frecuencia

        for token in self.vocabulario:

            if token in contador:

                self.frecuencias[
                    token
                ] = contador[token]

        self._reconstruir_indices()

        return self.resumen()

    # ======================================================
    # AGREGAR TOKENS
    # ======================================================

    def agregar_tokens(
        self,
        tokens: Iterable[str]
    ) -> int:

        agregados = 0

        for token in tokens:

            token = self._a_texto(
                token
            ).strip()

            if self.minusculas:
                token = token.lower()

            if not token:
                continue

            if token in self.token_a_id:
                continue

            if (
                len(self.vocabulario)
                >= self.vocab_size
            ):
                break

            self.vocabulario.append(
                token
            )

            self.frecuencias[
                token
            ] = 0

            agregados += 1

        if agregados:
            self._reconstruir_indices()

        return agregados

    # ======================================================
    # TOKENIZAR
    # ======================================================

    def tokenizar(
        self,
        texto: Any,
        agregar_nuevos: bool = False,
        modo_codigo: Optional[bool] = None
    ) -> List[str]:

        tokens = self.pretokenizar(
            texto,
            modo_codigo=modo_codigo
        )

        if agregar_nuevos:

            self.agregar_tokens(
                tokens
            )

        return tokens

    # ======================================================
    # CODIFICAR
    # ======================================================

    def codificar(
        self,
        texto: Any,
        agregar_bos: bool = True,
        agregar_eos: bool = True,
        longitud_maxima: Optional[int] = None,
        rellenar: bool = False,
        modo_codigo: Optional[bool] = None
    ) -> List[int]:

        tokens = self.tokenizar(
            texto,
            modo_codigo=modo_codigo
        )

        identificadores: List[int] = []

        if agregar_bos:

            identificadores.append(
                self.token_a_id[
                    "<BOS>"
                ]
            )

        id_desconocido = self.token_a_id[
            "<UNK>"
        ]

        for token in tokens:

            identificadores.append(
                self.token_a_id.get(
                    token,
                    id_desconocido
                )
            )

        if agregar_eos:

            identificadores.append(
                self.token_a_id[
                    "<EOS>"
                ]
            )

        if longitud_maxima is not None:

            longitud_maxima = max(
                1,
                int(longitud_maxima)
            )

            identificadores = identificadores[
                :longitud_maxima
            ]

            if (
                rellenar
                and len(identificadores)
                < longitud_maxima
            ):

                cantidad_relleno = (
                    longitud_maxima
                    - len(identificadores)
                )

                identificadores.extend(
                    [
                        self.token_a_id[
                            "<PAD>"
                        ]
                    ]
                    * cantidad_relleno
                )

        return identificadores

    # ======================================================
    # DECODIFICAR
    # ======================================================

    def decodificar(
        self,
        identificadores: Sequence[int],
        omitir_especiales: bool = True,
        restaurar_formato_codigo: bool = True
    ) -> str:

        tokens: List[str] = []

        especiales_omitibles = {
            "<PAD>",
            "<UNK>",
            "<BOS>",
            "<EOS>",
            "<CODE_START>",
            "<CODE_END>"
        }

        for identificador in identificadores:

            token = self.id_a_token.get(
                int(identificador),
                "<UNK>"
            )

            if (
                omitir_especiales
                and token in especiales_omitibles
            ):
                continue

            tokens.append(
                token
            )

        return self._unir_tokens(
            tokens,
            restaurar_formato_codigo
        )

    # ======================================================
    # UNIR TOKENS
    # ======================================================

    @staticmethod
    def _unir_tokens(
        tokens: Sequence[str],
        restaurar_formato_codigo: bool = True
    ) -> str:

        if not tokens:
            return ""

        texto = " ".join(
            tokens
        )

        texto = re.sub(
            r"\s+([.,;:!?%)\]}])",
            r"\1",
            texto
        )

        texto = re.sub(
            r"([¿¡([{])\s+",
            r"\1",
            texto
        )

        if restaurar_formato_codigo:

            texto = texto.replace(
                " <NEWLINE> ",
                "\n"
            )

            texto = texto.replace(
                "<NEWLINE>",
                "\n"
            )

            texto = texto.replace(
                " <TAB> ",
                "\t"
            )

            texto = texto.replace(
                "<TAB>",
                "\t"
            )

        texto = re.sub(
            r"[ ]+",
            " ",
            texto
        )

        return texto.strip()

    # ======================================================
    # CODIFICAR LOTE
    # ======================================================

    def codificar_lote(
        self,
        textos: Iterable[Any],
        longitud_maxima: Optional[int] = None,
        rellenar: bool = False,
        modo_codigo: Optional[bool] = None
    ) -> List[List[int]]:

        return [
            self.codificar(
                texto,
                longitud_maxima=longitud_maxima,
                rellenar=rellenar,
                modo_codigo=modo_codigo
            )
            for texto in textos
        ]

    # ======================================================
    # CONSULTAS
    # ======================================================

    def token_existe(
        self,
        token: str
    ) -> bool:

        return token in self.token_a_id

    def obtener_id(
        self,
        token: str
    ) -> int:

        return self.token_a_id.get(
            token,
            self.token_a_id["<UNK>"]
        )

    def obtener_token(
        self,
        identificador: int
    ) -> str:

        return self.id_a_token.get(
            int(identificador),
            "<UNK>"
        )

    # ======================================================
    # CAMBIAR MODO DE MAYUSCULAS
    # ======================================================

    def preservar_mayusculas(
        self,
        preservar: bool = True
    ) -> None:

        self.minusculas = not bool(
            preservar
        )

    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(
        self
    ) -> bool:

        directorio = os.path.dirname(
            self.archivo_vocabulario
        )

        if directorio:

            os.makedirs(
                directorio,
                exist_ok=True
            )

        contenido = {
            "version": self.VERSION,
            "vocab_size": self.vocab_size,
            "minusculas": self.minusculas,
            "vocabulario": self.vocabulario,
            "frecuencias": self.frecuencias
        }

        archivo_temporal = None

        try:

            descriptor, archivo_temporal = (
                tempfile.mkstemp(
                    prefix="vocabulario_",
                    suffix=".tmp",
                    dir=directorio or "."
                )
            )

            with os.fdopen(
                descriptor,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    contenido,
                    archivo,
                    ensure_ascii=False,
                    indent=4
                )

            os.replace(
                archivo_temporal,
                self.archivo_vocabulario
            )

            return True

        except (
            OSError,
            TypeError,
            ValueError
        ):

            if (
                archivo_temporal
                and os.path.exists(
                    archivo_temporal
                )
            ):

                try:

                    os.remove(
                        archivo_temporal
                    )

                except OSError:

                    pass

            return False

    # ======================================================
    # CARGAR
    # ======================================================

    def cargar(
        self
    ) -> bool:

        if not os.path.exists(
            self.archivo_vocabulario
        ):
            return False

        try:

            with open(
                self.archivo_vocabulario,
                "r",
                encoding="utf-8"
            ) as archivo:

                contenido = json.load(
                    archivo
                )

            vocabulario = contenido.get(
                "vocabulario"
            )

            if not isinstance(
                vocabulario,
                list
            ):

                raise ValueError(
                    "El vocabulario guardado "
                    "no es válido."
                )

            if "minusculas" in contenido:

                self.minusculas = bool(
                    contenido["minusculas"]
                )

            vocabulario_limpio: List[str] = []

            tokens_vistos = set()

            tokens_guardados = (
                self.TOKENS_ESPECIALES
                + vocabulario
            )

            for token in tokens_guardados:

                if (
                    isinstance(token, str)
                    and token not in tokens_vistos
                ):

                    vocabulario_limpio.append(
                        token
                    )

                    tokens_vistos.add(
                        token
                    )

                if (
                    len(vocabulario_limpio)
                    >= self.vocab_size
                ):

                    break

            self.vocabulario = (
                vocabulario_limpio
            )

            frecuencias = contenido.get(
                "frecuencias",
                {}
            )

            self.frecuencias = {
                token: int(
                    frecuencias.get(
                        token,
                        0
                    )
                )
                for token in self.vocabulario
            }

            self._reconstruir_indices()

            return True

        except (
            OSError,
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):

            self._reiniciar_vocabulario()

            return False

    # ======================================================
    # EXPORTAR
    # ======================================================

    def exportar(
        self
    ) -> Dict[str, Any]:

        return {
            "version": self.VERSION,
            "vocab_size": self.vocab_size,
            "minusculas": self.minusculas,
            "vocabulario": list(
                self.vocabulario
            ),
            "frecuencias": dict(
                self.frecuencias
            )
        }

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(
        self
    ) -> Dict[
        str,
        Union[str, int, bool]
    ]:

        return {
            "version": self.VERSION,
            "limite_vocabulario":
                self.vocab_size,
            "tokens_registrados":
                len(self.vocabulario),
            "preserva_mayusculas":
                not self.minusculas,
            "soporte_codigo":
                True
        }


# Nombres alternativos compatibles
Tokenizador = TokenizadorDraym
NativeSubwordTokenizer = TokenizadorDraym
