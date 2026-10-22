# ==========================================================
# DRAYMSYSTEM IA
# AGENTE ANALISTA
# ==========================================================

from datetime import datetime

from agentes.agente_general import AgenteGeneral


class AgenteAnalista(AgenteGeneral):

    INTENT_TAG = "analista"

    AGENT_LEVEL = 4

    ROLE = "analista"

    SPECIALTIES = [
        "analisis",
        "requisitos",
        "investigacion",
        "objetivos",
        "problemas",
        "riesgos",
        "procesos",
        "negocio",
        "planificacion"
    ]

    PALABRAS_CLAVE = {
        "analizar",
        "analisis",
        "problema",
        "requisito",
        "objetivo",
        "investigar",
        "riesgo",
        "proceso",
        "negocio",
        "estrategia",
        "plan",
        "evaluar",
        "diagnostico",
        "mejora",
        "solucion"
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
    # EXTRAER OBJETIVO
    # ======================================================

    def extraer_objetivo(
        self,
        tarea
    ):

        return str(
            tarea
        ).strip()

    # ======================================================
    # IDENTIFICAR RIESGOS
    # ======================================================

    def identificar_riesgos(
        self,
        tarea
    ):

        texto = str(
            tarea
        ).lower()

        riesgos = []

        if "seguridad" in texto:

            riesgos.append(
                "Seguridad"
            )

        if "eliminar" in texto:

            riesgos.append(
                "Perdida de informacion"
            )

        if "reemplazar" in texto:

            riesgos.append(
                "Impacto sobre componentes existentes"
            )

        if "automatico" in texto:

            riesgos.append(
                "Automatizacion sin supervision"
            )

        return riesgos

    # ======================================================
    # ANALISIS BASICO
    # ======================================================

    def analizar(
        self,
        tarea
    ):

        objetivo = (
            self.extraer_objetivo(
                tarea
            )
        )

        riesgos = (
            self.identificar_riesgos(
                tarea
            )
        )

        return {

            "objetivo":
                objetivo,

            "riesgos":
                riesgos,

            "nivel_riesgo":
                self.calcular_nivel_riesgo(
                    riesgos
                ),

            "acciones_recomendadas":
                self.generar_acciones(
                    objetivo
                )
        }

    # ======================================================
    # CALCULAR RIESGO
    # ======================================================

    def calcular_nivel_riesgo(
        self,
        riesgos
    ):

        cantidad = len(
            riesgos
        )

        if cantidad == 0:
            return "bajo"

        if cantidad <= 2:
            return "medio"

        if cantidad <= 4:
            return "alto"

        return "critico"

    # ======================================================
    # GENERAR ACCIONES
    # ======================================================

    def generar_acciones(
        self,
        objetivo
    ):

        return [

            "analizar_requisitos",

            "identificar_riesgos",

            "proponer_solucion",

            "validar_resultados",

            "documentar_conclusiones"
        ]

    # ======================================================
    # RESOLVER
    # ======================================================

    def resolver(
        self,
        tarea,
        contexto
    ):

        analisis = (
            self.analizar(
                tarea
            )
        )

        return {

            "agente":
                self.INTENT_TAG,

            "estado":
                "completada",

            "tarea":
                tarea,

            "analisis":
                analisis,

            "resultado":
                (
                    "Analisis completado "
                    "correctamente."
                ),

            "contexto":
                contexto
        }

    # ======================================================
    # GENERAR RESUMEN EJECUTIVO
    # ======================================================

    def resumen_ejecutivo(
        self,
        tarea
    ):

        analisis = self.analizar(
            tarea
        )

        return {

            "objetivo":
                analisis["objetivo"],

            "riesgos":
                analisis["riesgos"],

            "nivel":
                analisis["nivel_riesgo"]
        }

    # ======================================================
    # RESUMEN DEL AGENTE
    # ======================================================

    def resumen(self):

        datos = super().resumen()

        datos["tipo"] = (
            "analisis_y_requisitos"
        )

        return datos


# Compatibilidad
AgenteRequisitos = AgenteAnalista
