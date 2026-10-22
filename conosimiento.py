# ==========================================================
# DRAYMSYSTEM IA
# BASE DE CONOCIMIENTO
# ==========================================================

class KnowledgeBase:

    def __init__(self):

        self.conocimiento = {}

    # ======================================================
    # AGREGAR
    # ======================================================

    def agregar(
        self,
        tema,
        contenido
    ):

        self.conocimiento[tema] = contenido

    # ======================================================
    # OBTENER
    # ======================================================

    def obtener(
        self,
        tema,
        valor_default=None
    ):

        return self.conocimiento.get(
            tema,
            valor_default
        )

    # ======================================================
    # EXISTE
    # ======================================================

    def existe(
        self,
        tema
    ):

        return tema in self.conocimiento

    # ======================================================
    # ELIMINAR
    # ======================================================

    def eliminar(
        self,
        tema
    ):

        if tema in self.conocimiento:
            del self.conocimiento[tema]

    # ======================================================
    # LISTAR
    # ======================================================

    def listar_temas(self):

        return list(
            self.conocimiento.keys()
        )

    # ======================================================
    # CANTIDAD
    # ======================================================

    def cantidad(self):

        return len(
            self.conocimiento
        )
