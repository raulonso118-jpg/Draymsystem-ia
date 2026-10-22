# ==========================================================
# DRAYMSYSTEM IA
# GESTOR DE CONTEXTO
# ==========================================================

class ContextManager:

    def __init__(self):

        self.contexto = {}

    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(
        self,
        clave,
        valor
    ):

        self.contexto[clave] = valor

    # ======================================================
    # OBTENER
    # ======================================================

    def obtener(
        self,
        clave,
        valor_default=None
    ):

        return self.contexto.get(
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

        return clave in self.contexto

    # ======================================================
    # ELIMINAR
    # ======================================================

    def eliminar(
        self,
        clave
    ):

        if clave in self.contexto:
            del self.contexto[clave]

    # ======================================================
    # LIMPIAR
    # ======================================================

    def limpiar(self):

        self.contexto.clear()

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        return {
            "total_elementos": len(
                self.contexto
            ),
            "claves": list(
                self.contexto.keys()
            )
        }
