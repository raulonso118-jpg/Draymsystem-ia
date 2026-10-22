# ==========================================================
# DRAYMSYSTEM IA
# MOTOR MATEMATICO
# ==========================================================

import math
from typing import Dict, List, Iterable, Optional


class MotorMatematico:

    """
    Utilidades matemáticas para:

    - IA
    - Agentes
    - Razonamiento
    - Aprendizaje
    - Ranking
    - Estadísticas
    """

    VERSION = "1.0"

    # ======================================================
    # SUMA
    # ======================================================

    @staticmethod
    def suma(
        valores: Iterable[float]
    ) -> float:

        return sum(valores)

    # ======================================================
    # PROMEDIO
    # ======================================================

    @staticmethod
    def promedio(
        valores: Iterable[float]
    ) -> float:

        valores = list(valores)

        if not valores:
            return 0.0

        return sum(valores) / len(valores)

    # ======================================================
    # MEDIANA
    # ======================================================

    @staticmethod
    def mediana(
        valores: Iterable[float]
    ) -> float:

        valores = sorted(list(valores))

        if not valores:
            return 0.0

        n = len(valores)

        medio = n // 2

        if n % 2 == 0:

            return (
                valores[medio - 1]
                + valores[medio]
            ) / 2

        return valores[medio]

    # ======================================================
    # VARIANZA
    # ======================================================

    @classmethod
    def varianza(
        cls,
        valores: Iterable[float]
    ) -> float:

        valores = list(valores)

        if len(valores) < 2:
            return 0.0

        media = cls.promedio(valores)

        return sum(
            (
                valor - media
            ) ** 2
            for valor in valores
        ) / len(valores)

    # ======================================================
    # DESVIACION ESTANDAR
    # ======================================================

    @classmethod
    def desviacion_estandar(
        cls,
        valores: Iterable[float]
    ) -> float:

        return math.sqrt(
            cls.varianza(valores)
        )

    # ======================================================
    # NORMALIZAR VALOR
    # ======================================================

    @staticmethod
    def normalizar(
        valor: float,
        minimo: float,
        maximo: float
    ) -> float:

        if maximo == minimo:
            return 0.0

        return (
            valor - minimo
        ) / (
            maximo - minimo
        )

    # ======================================================
    # DISTANCIA EUCLIDIANA
    # ======================================================

    @staticmethod
    def distancia_euclidiana(
        a: List[float],
        b: List[float]
    ) -> float:

        if len(a) != len(b):

            raise ValueError(
                "Los vectores deben tener "
                "igual longitud."
            )

        suma = 0.0

        for x, y in zip(a, b):

            suma += (
                x - y
            ) ** 2

        return math.sqrt(suma)

    # ======================================================
    # PRODUCTO PUNTO
    # ======================================================

    @staticmethod
    def producto_punto(
        a: List[float],
        b: List[float]
    ) -> float:

        if len(a) != len(b):

            raise ValueError(
                "Los vectores deben tener "
                "igual longitud."
            )

        return sum(
            x * y
            for x, y in zip(a, b)
        )

    # ======================================================
    # NORMA VECTORIAL
    # ======================================================

    @staticmethod
    def norma(
        vector: List[float]
    ) -> float:

        return math.sqrt(
            sum(
                valor ** 2
                for valor in vector
            )
        )

    # ======================================================
    # SIMILITUD COSENO
    # ======================================================

    @classmethod
    def similitud_coseno(
        cls,
        a: List[float],
        b: List[float]
    ) -> float:

        norma_a = cls.norma(a)

        norma_b = cls.norma(b)

        if norma_a == 0:
            return 0.0

        if norma_b == 0:
            return 0.0

        return (
            cls.producto_punto(a, b)
            /
            (
                norma_a * norma_b
            )
        )

    # ======================================================
    # SOFTMAX
    # ======================================================

    @staticmethod
    def softmax(
        valores: List[float]
    ) -> List[float]:

        if not valores:
            return []

        maximo = max(valores)

        exp = [
            math.exp(
                valor - maximo
            )
            for valor in valores
        ]

        suma_exp = sum(exp)

        return [
            valor / suma_exp
            for valor in exp
        ]

    # ======================================================
    # PONDERACION
    # ======================================================

    @staticmethod
    def puntuacion_ponderada(
        criterios: Dict[str, float],
        pesos: Dict[str, float]
    ) -> float:

        puntuacion = 0.0

        for criterio, valor in criterios.items():

            peso = pesos.get(
                criterio,
                0.0
            )

            puntuacion += (
                valor * peso
            )

        return puntuacion

    # ======================================================
    # RANKING
    # ======================================================

    @staticmethod
    def ranking(
        elementos: Dict[str, float],
        descendente: bool = True
    ):

        return sorted(
            elementos.items(),
            key=lambda x: x[1],
            reverse=descendente
        )

    # ======================================================
    # PORCENTAJE
    # ======================================================

    @staticmethod
    def porcentaje(
        valor: float,
        total: float
    ) -> float:

        if total == 0:
            return 0.0

        return (
            valor / total
        ) * 100

    # ======================================================
    # ACTUALIZAR PROMEDIO
    # ======================================================

    @staticmethod
    def promedio_incremental(
        promedio_actual: float,
        cantidad: int,
        nuevo_valor: float
    ) -> float:

        if cantidad < 1:
            return nuevo_valor

        return (
            (
                promedio_actual
                * cantidad
            )
            + nuevo_valor
        ) / (
            cantidad + 1
        )

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        return {
            "version":
                self.VERSION,

            "funciones": [
                "promedio",
                "mediana",
                "varianza",
                "desviacion_estandar",
                "normalizar",
                "distancia_euclidiana",
                "producto_punto",
                "similitud_coseno",
                "softmax",
                "ranking",
                "porcentaje"
            ]
        }


# Compatibilidad
Matematicas = MotorMatematico
MotorMatematicas = MotorMatematico
