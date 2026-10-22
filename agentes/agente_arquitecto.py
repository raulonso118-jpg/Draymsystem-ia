# ==========================================================
# DRAYMSYSTEM IA
# AGENTE ARQUITECTO
# ==========================================================

from datetime import datetime

from agentes.agente_general import AgenteGeneral


class AgenteArquitecto(AgenteGeneral):

    INTENT_TAG = "arquitecto"

    AGENT_LEVEL = 4

    ROLE = "arquitecto_de_sistemas"

    SPECIALTIES = [
        "arquitectura",
        "diseño",
        "sistemas",
        "modulos",
        "patrones",
        "microservicios",
        "estructura",
        "integracion",
        "escalabilidad"
    ]

    PALABRAS_CLAVE = {
        "arquitectura",
        "arquitecto",
        "estructura",
        "sistema",
        "modulo",
        "modulos",
        "componente",
        "componentes",
        "diseño",
        "diseno",
        "patron",
        "patrones",
        "api",
        "microservicio",
        "escalabilidad",
        "integracion",
        "framework"
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

        for palabra in self.PALABRAS_CLAVE:

            if palabra in texto:
                return True

        return False

    # ======================================================
    # IDENTIFICAR TIPO
    # ======================================================

    def identificar_tipo_sistema(
        self,
        tarea
    ):

        texto = str(
            tarea
        ).lower()

        if "api" in texto:
            return "api"

        if "microservicio" in texto:
            return "microservicios"

        if "ia" in texto:
            return "inteligencia_artificial"

        if "web" in texto:
            return "web"

        return "general"

    # ======================================================
    # GENERAR ARQUITECTURA
    # ======================================================

    def generar_arquitectura(
        self,
        tipo
    ):

        return {

            "tipo": tipo,

            "capas": [
                "presentacion",
                "orquestacion",
                "negocio",
                "persistencia"
            ],

            "componentes": [
                "controladores",
                "servicios",
                "repositorios",
                "utilidades"
            ],

            "objetivos": [
                "escalabilidad",
                "mantenibilidad",
                "modularidad"
            ]
        }

    # ======================================================
    # VALIDAR ARQUITECTURA
    # ======================================================

    def validar_arquitectura(
        self,
        arquitectura
    ):

        errores = []

        if "capas" not in arquitectura:

            errores.append(
                "Faltan capas."
            )

        if "componentes" not in arquitectura:

            errores.append(
                "Faltan componentes."
            )

        return errores

    # ======================================================
    # RESOLVER
    # ======================================================

    def resolver(
        self,
        tarea,
        contexto
    ):

        tipo = (
            self.identificar_tipo_sistema(
                tarea
            )
        )

        arquitectura = (
            self.generar_arquitectura(
                tipo
            )
        )

        errores = (
            self.validar_arquitectura(
                arquitectura
            )
        )

        return {

            "agente":
                self.INTENT_TAG,

            "estado":
                "completada",

            "tarea":
                tarea,

            "tipo":
                tipo,

            "arquitectura":
                arquitectura,

            "validacion":
                errores,

            "resultado":
                (
                    "Arquitectura generada "
                    "correctamente."
                ),

            "contexto":
                contexto
        }

    # ======================================================
    # DISEÑO DE MODULOS
    # ======================================================

    def proponer_modulos(
        self,
        nombre_proyecto
    ):

        return [
            {
                "nombre":
                    "core",
                "responsabilidad":
                    "logica_central"
            },
            {
                "nombre":
                    "agentes",
                "responsabilidad":
                    "especialistas"
            },
            {
                "nombre":
                    "motor_ia",
                "responsabilidad":
                    "inteligencia"
            },
            {
                "nombre":
                    "datos",
                "responsabilidad":
                    "persistencia"
            }
        ]

    # ======================================================
    # RESUMEN
    # ======================================================

    def resumen(self):

        datos = super().resumen()

        datos["tipo"] = (
            "arquitectura_de_software"
        )

        return datos


# Compatibilidad
ArquitectoSoftware = AgenteArquitecto
