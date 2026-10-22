# ==========================================================
# DRAYMSYSTEM IA
# MEMORIA CENTRAL
# ==========================================================

import json
import os

from core.configuracion import DraymConfig


class MemoryManager:

    def __init__(self):

        self.file_path = DraymConfig.MEMORY_FILE

        self.data = {
            "proyectos": {},
            "conceptos": {},
            "preferencias": {},
            "historial": [],
            "aprendizaje": {}
        }

        self.cargar()

    # ======================================================
    # CARGA
    # ======================================================

    def cargar(self):

        if not os.path.exists(self.file_path):
            self.guardar()
            return

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as archivo:

                self.data = json.load(archivo)

        except Exception as error:

            print(
                f"[MEMORIA] Error cargando memoria: {error}"
            )

    # ======================================================
    # GUARDADO
    # ======================================================

    def guardar(self):

        try:

            os.makedirs(
                os.path.dirname(self.file_path),
                exist_ok=True
            )

            with open(
                self.file_path,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    self.data,
                    archivo,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception as error:

            print(
                f"[MEMORIA] Error guardando memoria: {error}"
            )

    # ======================================================
    # CONCEPTOS
    # ======================================================

    def guardar_concepto(
        self,
        clave,
        valor
    ):

        self.data["conceptos"][clave] = valor

        self.guardar()

    def obtener_concepto(
        self,
        clave
    ):

        return self.data["conceptos"].get(clave)

    # ======================================================
    # PROYECTOS
    # ======================================================

    def guardar_proyecto(
        self,
        nombre,
        contenido
    ):

        self.data["proyectos"][nombre] = contenido

        self.guardar()

    def obtener_proyecto(
        self,
        nombre
    ):

        return self.data["proyectos"].get(nombre)

    # ======================================================
    # PREFERENCIAS
    # ======================================================

    def guardar_preferencia(
        self,
        clave,
        valor
    ):

        self.data["preferencias"][clave] = valor

        self.guardar()

    def obtener_preferencia(
        self,
        clave
    ):

        return self.data["preferencias"].get(clave)

    # ======================================================
    # HISTORIAL
    # ======================================================

    def agregar_historial(
        self,
        entrada
    ):

        self.data["historial"].append(entrada)

        self.guardar()

    # ======================================================
    # APRENDIZAJE
    # ======================================================

    def guardar_aprendizaje(
        self,
        clave,
        valor
    ):

        self.data["aprendizaje"][clave] = valor

        self.guardar()

    def obtener_aprendizaje(
        self,
        clave
    ):

        return self.data["aprendizaje"].get(clave)
