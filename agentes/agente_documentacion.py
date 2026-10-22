# ==========================================================
# DRAYMSYSTEM IA
# AGENTE DOCUMENTACION
# ==========================================================

from datetime import datetime

from agentes.agente_general import AgenteGeneral


class AgenteDocumentacion(AgenteGeneral):

    INTENT_TAG = "documentacion"

    AGENT_LEVEL = 3

    ROLE = "documentador"

    SPECIALTIES = [
        "documentacion",
        "manuales",
        "guias",
        "api",
        "markdown",
        "readme",
        "explicaciones",
        "tutoriales",
        "diagramas"
    ]

    PALABRAS_CLAVE = {
        "documentacion",
        "documentar",
        "manual",
        "guia",
        "readme",
        "explicar",
        "explicacion",
        "tutorial",
        "api",
        "referencia",
        "markdown",
        "wiki",
        "instructivo"
    }

    def __init__(self):

        super().__init__()

        self.fecha_creacion = (
            datetime.now()
        )

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
    # IDENTIFICAR TIPO
    # ======================================================

    def identificar_documento(
        self,
        tarea
    ):

        texto = str(
            tarea
        ).lower()

        if "readme" in texto:
            return "readme"

        if "api" in texto:
            return "api"

        if "manual" in texto:
            return "manual"

        if "tutorial" in texto:
            return "tutorial"

        if "guia" in texto:
            return "guia"

        return "documentacion_general"

    # ======================================================
    # GENERAR ESTRUCTURA
    # ======================================================

    def generar_estructura(
        self,
        tipo
    ):

        estructuras = {

            "readme": [
                "descripcion",
                "instalacion",
                "uso",
                "ejemplos",
                "licencia"
            ],

            "api": [
                "introduccion",
                "endpoints",
                "parametros",
                "ejemplos",
                "errores"
            ],

            "manual": [
                "objetivo",
                "requisitos",
                "procedimiento",
                "validacion",
                "anexos"
            ]
        }

        return estructuras.get(
            tipo,
            [
                "introduccion",
                "contenido",
                "conclusion"
            ]
        )

    # ======================================================
    # VALIDAR DOCUMENTACION
    # ======================================================

    def validar_documentacion(
        self,
        estructura
    ):

        observaciones = []

        if len(estructura) < 3:

            observaciones.append(
                "La documentación es demasiado corta."
            )

        return observaciones

    # ======================================================
    # RESOLVER
    # ======================================================

    def resolver(
        self,
        tarea,
        contexto
    ):

        tipo = self.identificar_documento(
            tarea
        )

        estructura = (
            self.generar_estructura(
                tipo
            )
        )

        observaciones = (
            self.validar_documentacion(
                estructura
            )
        )

        return {

            "agente":
                self.INTENT_TAG,

            "estado":
                "completada",

            "tarea":
                tarea,

            "tipo_documento":
                tipo,

            "estructura":
                estructura,

            "observaciones":
                observaciones,

            "resultado":
                (
                    "Estructura de documentación "
                    "generada correctamente."
                ),

            "contexto":
                contexto
        }

    # ======================================================
    # CREAR PLANTILLA
    # ======================================================

    def crear_plantilla(
        self,
        titulo,
        secciones
    ):

        documento = (
            f"# {titulo}\n\n"
        )

        for seccion in secciones:

            documento += (
                f"## {seccion}\n\n"
            )

        return documento

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        datos = super().resumen()

        datos["tipo"] = (
            "documentacion_tecnica"
        )

        return datos


# Compatibilidad
AgenteDocs = AgenteDocumentacion
Documentador = AgenteDocumentacion
