# motor_ia/selector_agentes.py

import json
import os
from typing import Dict, Any, List


class SelectorAgentes:
    """
    Selecciona el mejor agente para una tarea.

    Factores:
    - especialidad
    - experiencia
    - éxitos
    - fallos
    - nivel
    """

    def __init__(
        self,
        archivo_metricas="datos/agentes/metricas_agentes.json"
    ):
        self.archivo_metricas = archivo_metricas
        self.metricas = self._cargar_metricas()

    # ==================================================
    # Persistencia
    # ==================================================

    def _cargar_metricas(self):

        if os.path.exists(self.archivo_metricas):
            try:
                with open(
                    self.archivo_metricas,
                    "r",
                    encoding="utf-8"
                ) as f:
                    return json.load(f)
            except Exception:
                pass

        return {}

    def guardar(self):

        os.makedirs(
            os.path.dirname(self.archivo_metricas),
            exist_ok=True
        )

        with open(
            self.archivo_metricas,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                self.metricas,
                f,
                ensure_ascii=False,
                indent=4
            )

    # ==================================================
    # Registro
    # ==================================================

    def registrar_agente(self, agente):

        nombre = agente.INTENT_TAG

        if nombre not in self.metricas:

            self.metricas[nombre] = {
                "exitos": 0,
                "fallos": 0,
                "experiencia": 0,
                "selecciones": 0
            }

            self.guardar()

    # ==================================================
    # Métricas
    # ==================================================

    def registrar_exito(self, nombre):

        if nombre in self.metricas:
            self.metricas[nombre]["exitos"] += 1
            self.metricas[nombre]["experiencia"] += 2
            self.guardar()

    def registrar_fallo(self, nombre):

        if nombre in self.metricas:
            self.metricas[nombre]["fallos"] += 1
            self.guardar()

    # ==================================================
    # Puntuación
    # ==================================================

    def calcular_puntuacion(
        self,
        nombre,
        especialidades=None,
        tarea_tag=None
    ) -> float:

        datos = self.metricas.get(
            nombre,
            {}
        )

        exitos = datos.get("exitos", 0)
        fallos = datos.get("fallos", 0)
        experiencia = datos.get("experiencia", 0)

        puntuacion = float(exitos - fallos) + experiencia * 0.1

        if (
            tarea_tag
            and especialidades
            and tarea_tag in especialidades
        ):
            puntuacion += 10.0

        return puntuacion

    def seleccionar(
        self,
        candidatos: List[Any],
        tarea_tag=None
    ):

        if not candidatos:
            return None

        def puntuar(agente):

            nombre = getattr(agente, "INTENT_TAG", None) or agente.__class__.__name__

            return self.calcular_puntuacion(
                nombre,
                getattr(agente, "SPECIALTIES", None),
                tarea_tag
            )

        return max(
            candidatos,
            key=puntuar
        )
