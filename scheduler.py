# motor_ia/scheduler.py

import json
import os
from typing import List, Dict, Any


class Scheduler:

    """
    Administrador de ejecución de tareas.

    Responsabilidades:

    - Prioridades
    - Dependencias
    - Reintentos
    - Estado de ejecución
    """

    ARCHIVO_ESTADO = "datos/tareas/scheduler_estado.json"

    def __init__(self):

        self.estado = {
            "pendientes": [],
            "ejecutando": [],
            "finalizadas": [],
            "fallidas": []
        }

        self._cargar_estado()

    # ==================================================
    # Persistencia
    # ==================================================

    def _cargar_estado(self):

        if os.path.exists(self.ARCHIVO_ESTADO):

            try:

                with open(
                    self.ARCHIVO_ESTADO,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    self.estado = json.load(archivo)

            except Exception:
                pass

    def guardar_estado(self):

        os.makedirs(
            os.path.dirname(self.ARCHIVO_ESTADO),
            exist_ok=True
        )

        with open(
            self.ARCHIVO_ESTADO,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                self.estado,
                archivo,
                indent=4,
                ensure_ascii=False
            )

    # ==================================================
    # Registro
    # ==================================================

    def registrar_tarea(
        self,
        nombre: str,
        prioridad: int = 1,
        dependencias: List[str] = None,
        max_intentos: int = 3
    ):

        if dependencias is None:
            dependencias = []

        tarea = {
            "nombre": nombre,
            "prioridad": prioridad,
            "dependencias": dependencias,
            "intentos": 0,
            "max_intentos": max_intentos,
            "estado": "pendiente"
        }

        self.estado["pendientes"].append(tarea)

        self.guardar_estado()

    # ==================================================
    # Dependencias
    # ==================================================

    def dependencias_cumplidas(
        self,
        tarea: Dict[str, Any]
    ) -> bool:

        finalizadas = {
            t["nombre"]
            for t in self.estado["finalizadas"]
        }

        for dep in tarea["dependencias"]:

            if dep not in finalizadas:
                return False

        return True

    # ==================================================
    # Próxima tarea
    # ==================================================

    def obtener_siguiente_tarea(self):

        candidatas = []

        for tarea in self.estado["pendientes"]:

            if self.dependencias_cumplidas(tarea):
                candidatas.append(tarea)

        if not candidatas:
            return None

        candidatas.sort(
            key=lambda x: x["prioridad"]
        )

        siguiente = candidatas[0]

        self.estado["pendientes"].remove(
            siguiente
        )

        siguiente["estado"] = "ejecutando"

        self.estado["ejecutando"].append(
            siguiente
        )

        self.guardar_estado()

        return siguiente

    # ==================================================
    # Finalización
    # ==================================================

    def marcar_completada(
        self,
        nombre_tarea: str
    ):

        for tarea in list(
            self.estado["ejecutando"]
        ):

            if tarea["nombre"] == nombre_tarea:

                tarea["estado"] = "finalizada"

                self.estado["ejecutando"].remove(
                    tarea
                )

                self.estado["finalizadas"].append(
                    tarea
                )

                break

        self.guardar_estado()

    # ==================================================
    # Error
    # ==================================================

    def marcar_fallida(
        self,
        nombre_tarea: str
    ):

        for tarea in list(
            self.estado["ejecutando"]
        ):

            if tarea["nombre"] != nombre_tarea:
                continue

            tarea["intentos"] += 1

            self.estado["ejecutando"].remove(
                tarea
            )

            if tarea["intentos"] >= tarea["max_intentos"]:

                tarea["estado"] = "fallida"

                self.estado["fallidas"].append(
                    tarea
                )

            else:

                tarea["estado"] = "pendiente"

                self.estado["pendientes"].append(
                    tarea
                )

            break

        self.guardar_estado()

    # ==================================================
    # Consultas
    # ==================================================

    def hay_trabajo(self):

        return len(
            self.estado["pendientes"]
        ) > 0

    def resumen(self):

        return {

            "pendientes":
                len(
                    self.estado["pendientes"]
                ),

            "ejecutando":
                len(
                    self.estado["ejecutando"]
                ),

            "finalizadas":
                len(
                    self.estado["finalizadas"]
                ),

            "fallidas":
                len(
                    self.estado["fallidas"]
                )
        }
