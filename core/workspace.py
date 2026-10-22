# ==========================================================
# DRAYMSYSTEM IA
# WORKSPACE COMPARTIDO
# ==========================================================

import json
import os


class SharedWorkspace:

    ARCHIVO_WORKSPACE = "datos/workspace/workspace.json"

    def __init__(self):

        self.workspace = {}

        self.cargar_disco()

    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(
        self,
        clave,
        contenido
    ):

        self.workspace[clave] = contenido

    # ======================================================
    # OBTENER
    # ======================================================

    def obtener(
        self,
        clave,
        valor_default=None
    ):

        return self.workspace.get(
            clave,
            valor_default
        )

    # ======================================================
    # EXISTE
    # ======================================================

    def existe(
        self,
        clave
    ):

        return clave in self.workspace

    # ======================================================
    # ELIMINAR
    # ======================================================

    def eliminar(
        self,
        clave
    ):

        if clave in self.workspace:
            del self.workspace[clave]

    # ======================================================
    # LIMPIAR
    # ======================================================

    def limpiar(self):

        self.workspace.clear()

    # ======================================================
    # LISTAR
    # ======================================================

    def listar_claves(self):

        return list(
            self.workspace.keys()
        )

    # ======================================================
    # RESUMEN
    # ======================================================

    def obtener_resumen(self):

        if not self.workspace:
            return "Workspace vacío"

        resultado = []

        for clave in self.workspace.keys():

            resultado.append(
                f"[{clave}]"
            )

        return "\n".join(resultado)

    # ======================================================
    # GUARDAR EN DISCO
    # ======================================================

    def guardar_disco(self):

        try:

            os.makedirs(
                os.path.dirname(
                    self.ARCHIVO_WORKSPACE
                ),
                exist_ok=True
            )

            with open(
                self.ARCHIVO_WORKSPACE,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    self.workspace,
                    archivo,
                    ensure_ascii=False,
                    indent=4
                )

            return True

        except Exception as error:

            print(
                f"Error guardando workspace: {error}"
            )

            return False

    # ======================================================
    # CARGAR DESDE DISCO
    # ======================================================

    def cargar_disco(self):

        try:

            if os.path.exists(
                self.ARCHIVO_WORKSPACE
            ):

                with open(
                    self.ARCHIVO_WORKSPACE,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    self.workspace = json.load(
                        archivo
                    )

            return True

        except Exception as error:

            print(
                f"Error cargando workspace: {error}"
            )

            self.workspace = {}

            return False

    # ======================================================
    # AUTOGUARDADO
    # ======================================================

    def sincronizar(self):

        self.guardar_disco()
