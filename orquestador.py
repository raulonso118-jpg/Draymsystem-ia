from __future__ import annotations

import inspect
import logging
import threading
import time
import uuid

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ==========================================================
# 1. IMPORTACIONES DEL NÚCLEO (Rutas exactas requeridas)
# ==========================================================

try:
    from core.configuracion import DraymConfig
except ImportError:
    class DraymConfig:
        SYSTEM_NAME = "DraymSystem IA"
        VERSION = "1.0.0"
        MAX_WORKERS = 4
        MAX_REINTENTOS = 2
        ACTIVAR_ENJAMBRE = True
        ACTIVAR_SUPERVISION = True
        ACTIVAR_MEMORIA = True


try:
    from core.memoria import MemoryManager
except ImportError:
    MemoryManager = None


try:
    from core.workspace import SharedWorkspace
except ImportError:
    SharedWorkspace = None


try:
    from core.registro_agentes import RegistroAgentes
except ImportError:
    RegistroAgentes = None


try:
    from core.enjambre import Enjambre
except ImportError:
    try:
        from core.enjambre import GestorEnjambre as Enjambre
    except ImportError:
        Enjambre = None


try:
    from core.supervisor import Supervisor
except ImportError:
    Supervisor = None


try:
    from core.integrador import Integrador
except ImportError:
    Integrador = None


# ==========================================================
# 2. IMPORTACIONES DEL MOTOR IA (Rutas exactas requeridas)
# ==========================================================

try:
    from motor_ia.contexto import ContextManager
except ImportError:
    ContextManager = None


try:
    from motor_ia.conocimiento import KnowledgeBase
except ImportError:
    KnowledgeBase = None


try:
    from motor_ia.analizador_tareas import AnalizadorTareas
except ImportError:
    AnalizadorTareas = None


try:
    from motor_ia.planner import Planner
except ImportError:
    Planner = None


# ==========================================================
# EXCEPCIONES
# ==========================================================

class ErrorOrquestador(Exception):
    """Error base producido durante la coordinación del sistema."""


class ErrorConfiguracion(ErrorOrquestador):
    """La arquitectura no cuenta con una configuración válida."""


class ErrorPlanificacion(ErrorOrquestador):
    """No fue posible producir un plan ejecutable."""


class ErrorSeleccionAgente(ErrorOrquestador):
    """No se encontró un agente compatible con una tarea."""


class ErrorEjecucionAgente(ErrorOrquestador):
    """Un agente no pudo ejecutar correctamente una tarea."""


# ==========================================================
# MODELOS INTERNOS
# ==========================================================

@dataclass
class TareaOrquestada:
    id: str
    nombre: str
    descripcion: str
    categoria: str = "general"
    especialidad: str = "general"
    prioridad: int = 100
    dependencias: List[str] = field(default_factory=list)
    contexto: Dict[str, Any] = field(default_factory=dict)
    metadatos: Dict[str, Any] = field(default_factory=dict)

    estado: str = "pendiente"
    agente: Optional[str] = None
    resultado: Any = None
    error: Optional[str] = None
    intentos: int = 0

    @classmethod
    def desde_objeto(
        cls,
        dato: Any,
        indice: int = 0,
        categoria_default: str = "general",
    ) -> "TareaOrquestada":

        if isinstance(dato, cls):
            return dato

        if isinstance(dato, str):
            return cls(
                id=f"tarea_{indice + 1}",
                nombre=f"Tarea {indice + 1}",
                descripcion=dato,
                categoria=categoria_default,
                especialidad=categoria_default,
                prioridad=indice + 1,
            )

        if isinstance(dato, Mapping):
            identificador = str(
                dato.get("id")
                or dato.get("tarea_id")
                or dato.get("identificador")
                or f"tarea_{indice + 1}"
            )

            nombre = str(
                dato.get("nombre")
                or dato.get("titulo")
                or dato.get("name")
                or identificador
            )

            descripcion = str(
                dato.get("descripcion")
                or dato.get("instruccion")
                or dato.get("objetivo")
                or dato.get("prompt")
                or nombre
            )

            categoria = str(
                dato.get("categoria")
                or dato.get("intencion")
                or dato.get("tipo")
                or categoria_default
            )

            especialidad = str(
                dato.get("especialidad")
                or dato.get("agente")
                or dato.get("tag")
                or dato.get("intent_tag")
                or categoria
            )

            dependencias = dato.get("dependencias", [])
            if isinstance(dependencias, str):
                dependencias = [dependencias]

            try:
                prioridad = int(dato.get("prioridad", indice + 1))
            except (TypeError, ValueError):
                prioridad = indice + 1

            return cls(
                id=identificador,
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                especialidad=especialidad,
                prioridad=prioridad,
                dependencias=list(dependencias or []),
                contexto=dict(dato.get("contexto", {}) or {}),
                metadatos=dict(dato.get("metadatos", {}) or {}),
            )

        return cls(
            id=f"tarea_{indice + 1}",
            nombre=f"Tarea {indice + 1}",
            descripcion=str(dato),
            categoria=categoria_default,
            especialidad=categoria_default,
            prioridad=indice + 1,
        )


@dataclass
class ResultadoEjecucion:
    id: str
    solicitud: str
    categoria: str
    estado: str
    respuesta: str
    tareas: List[Dict[str, Any]]
    errores: List[str]
    agentes_utilizados: List[str]
    modo_ejecucion: str
    inicio: float
    fin: float
    metadatos: Dict[str, Any] = field(default_factory=dict)

    @property
    def duracion(self) -> float:
        return max(0.0, self.fin - self.inicio)

    def como_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "solicitud": self.solicitud,
            "categoria": self.categoria,
            "estado": self.estado,
            "respuesta": self.respuesta,
            "tareas": self.tareas,
            "errores": self.errores,
            "agentes_utilizados": self.agentes_utilizados,
            "modo_ejecucion": self.modo_ejecucion,
            "duracion": self.duracion,
            "metadatos": self.metadatos,
        }


# ==========================================================
# COMPONENTES DE RESPALDO (Cumpliendo contratos exactos)
# ==========================================================

class MemoriaRespaldo:
    def __init__(self):
        self.data: Dict[str, Any] = {
            "solicitudes": [],
            "resultados": [],
            "errores": [],
        }

    def guardar(self, clave: str, valor: Any) -> None:
        self.data[clave] = valor

    def obtener(self, clave: str, valor_default: Any = None) -> Any:
        return self.data.get(clave, valor_default)

    def registrar_solicitud(self, solicitud: str) -> None:
        self.data["solicitudes"].append(solicitud)

    def registrar_resultado(self, resultado: Any) -> None:
        self.data["resultados"].append(resultado)

    def registrar_error(self, error: Any) -> None:
        self.data["errores"].append(error)

    def buscar_relevante(self, consulta: str) -> Any:
        return None


class WorkspaceRespaldo:
    def __init__(self):
        self.workspace: Dict[str, Any] = {}

    def guardar(self, clave: str, contenido: Any) -> None:
        self.workspace[clave] = contenido

    def actualizar(self, clave: str, contenido: Any) -> None:
        self.guardar(clave, contenido)

    def obtener(self, clave: str, valor_default: Any = None) -> Any:
        return self.workspace.get(clave, valor_default)

    def existe(self, clave: str) -> bool:
        return clave in self.workspace

    def eliminar(self, clave: str) -> None:
        self.workspace.pop(clave, None)

    def limpiar(self) -> None:
        self.workspace.clear()

    def listar_claves(self) -> List[str]:
        return list(self.workspace.keys())

    def obtener_resumen(self) -> str:
        if not self.workspace:
            return "Workspace vacío"

        return "\n".join(
            f"[{clave}]"
            for clave in self.workspace
        )


class RegistroRespaldo:
    def __init__(self):
        self._agentes: Dict[str, Any] = {}

    def registrar(self, agente: Any) -> None:
        tag = (
            getattr(agente, "INTENT_TAG", None)
            or getattr(agente, "intent_tag", None)
            or getattr(agente, "nombre", None)
            or agente.__class__.__name__.lower()
        )
        self._agentes[str(tag)] = agente

    def obtener(self, tag: str) -> Optional[Any]:
        return self._agentes.get(tag)

    def listar(self) -> List[Any]:
        return list(self._agentes.values())

    def buscar_compatibles(self, especialidad: str) -> List[Any]:
        compatibles = []

        for tag, agente in self._agentes.items():
            especialidades = getattr(
                agente,
                "SPECIALTIES",
                getattr(agente, "especialidades", []),
            )

            if isinstance(especialidades, str):
                especialidades = [especialidades]

            if especialidad == tag or especialidad in especialidades:
                compatibles.append(agente)

        if not compatibles:
            general = self._agentes.get("general")
            if general is not None:
                compatibles.append(general)

        return compatibles


class ContextoRespaldo:
    def __init__(self):
        self._contexto: Dict[str, Any] = {}

    def guardar(self, clave: str, valor: Any) -> None:
        self._contexto[clave] = valor

    def obtener(self, clave: str, valor_default: Any = None) -> Any:
        return self._contexto.get(clave, valor_default)

    def construir(self, solicitud: str, **extras: Any) -> Dict[str, Any]:
        contexto = dict(self._contexto)
        contexto.update(extras)
        contexto["solicitud"] = solicitud
        return contexto


class AnalizadorRespaldo:
    def analizar(self, solicitud: str) -> Dict[str, Any]:
        texto = solicitud.lower()

        categorias = {
            "codigo": (
                "código", "codigo", "programa", "python", "función",
                "funcion", "clase", "api", "software", "depura",
            ),
            "arquitectura": (
                "arquitectura", "sistema", "estructura", "módulo",
                "modulo", "diseño", "diseno",
            ),
            "investigacion": (
                "investiga", "investigación", "investigacion",
                "analiza", "fuentes",
            ),
            "documentacion": (
                "documenta", "manual", "documentación",
                "documentacion", "informe",
            ),
            "qa": (
                "prueba", "test", "verifica", "valida",
                "revisa", "error",
            ),
        }

        categoria = "general"

        for candidata, palabras in categorias.items():
            if any(palabra in texto for palabra in palabras):
                categoria = candidata
                break

        palabras = len(solicitud.split())

        if palabras > 120:
            complejidad = "alta"
        elif palabras > 35:
            complejidad = "media"
        else:
            complejidad = "baja"

        requiere_enjambre = (
            complejidad == "alta"
            or "completo" in texto
            or "proyecto" in texto
            or "sistema operativo" in texto
            or "libro" in texto
            or "varios agentes" in texto
            or "enjambre" in texto
        )

        return {
            "categoria": categoria,
            "complejidad": complejidad,
            "requiere_enjambre": requiere_enjambre,
            "solicitud": solicitud,
        }


class PlannerRespaldo:
    def crear_plan(
        self,
        categoria: str,
        solicitud: Optional[str] = None,
        analisis: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        descripcion = solicitud or categoria

        return [
            {
                "id": "tarea_1",
                "nombre": "Procesamiento principal",
                "descripcion": descripcion,
                "categoria": categoria,
                "especialidad": categoria,
                "prioridad": 1,
                "dependencias": [],
            }
        ]


class IntegradorRespaldo:
    def integrar(
        self,
        resultados: Sequence[Any],
        **_: Any,
    ) -> str:

        textos = []

        for resultado in resultados:
            if resultado is None:
                continue

            if isinstance(resultado, str):
                textos.append(resultado)
            elif isinstance(resultado, Mapping):
                textos.append(
                    str(
                        resultado.get("resultado")
                        or resultado.get("respuesta")
                        or resultado.get("contenido")
                        or resultado
                    )
                )
            else:
                textos.append(str(resultado))

        return "\n\n".join(textos).strip()


# ==========================================================
# ORQUESTADOR CENTRAL
# ==========================================================

class Orquestador:
    """
    Coordinador central de DraymSystem IA.
    La interfaz de usuario debe comunicarse exclusivamente a través de:
        orquestador.procesar("solicitud")
    """

    def __init__(
        self,
        memoria: Optional[Any] = None,
        workspace: Optional[Any] = None,
        registro: Optional[Any] = None,
        contexto: Optional[Any] = None,
        conocimiento: Optional[Any] = None,
        analizador: Optional[Any] = None,
        planner: Optional[Any] = None,
        enjambre: Optional[Any] = None,
        supervisor: Optional[Any] = None,
        integrador: Optional[Any] = None,
        max_workers: Optional[int] = None,
        max_reintentos: Optional[int] = None,
    ):

        self.nombre = getattr(
            DraymConfig,
            "SYSTEM_NAME",
            "DraymSystem IA",
        )

        self.version = getattr(
            DraymConfig,
            "VERSION",
            "1.0.0",
        )

        self.max_workers = int(
            max_workers
            or getattr(DraymConfig, "MAX_WORKERS", 4)
        )

        self.max_reintentos = int(
            max_reintentos
            or getattr(DraymConfig, "MAX_REINTENTOS", 2)
        )

        self.activar_enjambre = bool(
            getattr(DraymConfig, "ACTIVAR_ENJAMBRE", True)
        )

        self.activar_supervision = bool(
            getattr(DraymConfig, "ACTIVAR_SUPERVISION", True)
        )

        self.activar_memoria = bool(
            getattr(DraymConfig, "ACTIVAR_MEMORIA", True)
        )

        self.logger = logging.getLogger("DraymSystem.Orquestador")
        self._lock = threading.RLock()

        # Componentes del Núcleo obligatorios por contrato
        self.memoria = memoria or self._crear_componente(
            MemoryManager,
            MemoriaRespaldo,
        )

        self.workspace = workspace or self._crear_componente(
            SharedWorkspace,
            WorkspaceRespaldo,
        )

        self.registro = registro or self._crear_componente(
            RegistroAgentes,
            RegistroRespaldo,
        )

        # Componentes del Motor IA obligatorios por contrato
        self.contexto = contexto or self._crear_componente(
            ContextManager,
            ContextoRespaldo,
        )

        self.conocimiento = conocimiento or self._crear_componente(
            KnowledgeBase,
            lambda: None,
        )

        self.analizador = analizador or self._crear_componente(
            AnalizadorTareas,
            AnalizadorRespaldo,
        )

        self.planner = planner or self._crear_componente(
            Planner,
            PlannerRespaldo,
        )

        # Coordinación avanzada obligatoria
        self.enjambre = enjambre or self._crear_componente(
            Enjambre,
            lambda: None,
        )

        self.supervisor = supervisor or self._crear_componente(
            Supervisor,
            lambda: None,
        )

        self.integrador = integrador or self._crear_componente(
            Integrador,
            IntegradorRespaldo,
        )

        self._historial_operaciones: List[Dict[str, Any]] = []

        self._registrar_evento(
            "sistema_iniciado",
            {
                "nombre": self.nombre,
                "version": self.version,
            },
        )

    @staticmethod
    def _crear_componente(
        clase_principal: Optional[Any],
        fabrica_respaldo: Any,
    ) -> Any:

        if clase_principal is not None:
            try:
                return clase_principal()
            except Exception:
                pass

        return fabrica_respaldo()

    def registrar_agente(self, agente: Any) -> bool:
        if agente is None:
            raise ValueError("No se puede registrar un agente vacío.")

        # Verificar atributos obligatorios del agente
        for attr in ("INTENT_TAG", "SPECIALTIES", "AGENT_LEVEL"):
            if not hasattr(agente, attr):
                self.logger.warning(
                    f"El agente {agente.__class__.__name__} no define el atributo obligatorio '{attr}'."
                )

        metodos = (
            "registrar",
            "agregar",
            "registrar_agente",
            "add",
        )

        for metodo in metodos:
            funcion = getattr(self.registro, metodo, None)

            if callable(funcion):
                funcion(agente)

                self._registrar_evento(
                    "agente_registrado",
                    {"agente": self._nombre_agente(agente)},
                )

                return True

        raise ErrorConfiguracion(
            "El registro de agentes no tiene un método compatible "
            "para registrar agentes."
        )

    def registrar_agentes(self, agentes: Iterable[Any]) -> int:
        total = 0

        for agente in agentes:
            if self.registrar_agente(agente):
                total += 1

        return total

    def listar_agentes(self) -> List[Any]:
        metodos = (
            "listar",
            "listar_agentes",
            "obtener_todos",
            "todos",
        )

        for metodo in metodos:
            funcion = getattr(self.registro, metodo, None)

            if callable(funcion):
                resultado = funcion()

                if isinstance(resultado, Mapping):
                    return list(resultado.values())

                if resultado is None:
                    return []

                return list(resultado)

        posibles_atributos = (
            "agentes",
            "_agentes",
            "registro",
        )

        for atributo in posibles_atributos:
            contenido = getattr(self.registro, atributo, None)

            if isinstance(contenido, Mapping):
                return list(contenido.values())

            if isinstance(contenido, Sequence) and not isinstance(
                contenido,
                (str, bytes),
            ):
                return list(contenido)

        return []

    def procesar(
        self,
        solicitud: str,
        agente_preferido: Optional[str] = None,
        devolver_detalles: bool = False,
        contexto_adicional: Optional[Dict[str, Any]] = None,
    ) -> Any:

        inicio = time.time()
        operacion_id = uuid.uuid4().hex

        solicitud = self._validar_solicitud(solicitud)
        contexto_adicional = contexto_adicional or {}

        tareas: List[TareaOrquestada] = []
        errores: List[str] = []
        agentes_utilizados: List[str] = []
        categoria = "general"
        modo = "individual"

        try:
            self._preparar_operacion(
                operacion_id,
                solicitud,
                contexto_adicional,
            )

            analisis = self._analizar_solicitud(solicitud)
            categoria = str(analisis.get("categoria", "general"))

            contexto_global = self._construir_contexto(
                solicitud=solicitud,
                analisis=analisis,
                contexto_adicional=contexto_adicional,
            )

            plan_crudo = self._crear_plan(
                solicitud=solicitud,
                analisis=analisis,
                contexto=contexto_global,
            )

            tareas = self._normalizar_plan(
                plan_crudo,
                categoria_default=categoria,
                solicitud=solicitud,
            )

            requiere_enjambre = self._requiere_enjambre(
                analisis=analisis,
                tareas=tareas,
            )

            if requiere_enjambre:
                modo = "enjambre"
                resultados = self._ejecutar_enjambre(
                    tareas=tareas,
                    contexto_global=contexto_global,
                    agente_preferido=agente_preferido,
                    agentes_utilizados=agentes_utilizados,
                    errores=errores,
                )
            else:
                modo = "individual"
                resultados = self._ejecutar_plan(
                    tareas=tareas,
                    contexto_global=contexto_global,
                    agente_preferido=agente_preferido,
                    agentes_utilizados=agentes_utilizados,
                    errores=errores,
                )

            reporte_supervision = self._supervisar(
                solicitud=solicitud,
                analisis=analisis,
                tareas=tareas,
                resultados=resultados,
                contexto=contexto_global,
            )

            respuesta = self._integrar(
                solicitud=solicitud,
                analisis=analisis,
                tareas=tareas,
                resultados=resultados,
                supervision=reporte_supervision,
                contexto=contexto_global,
            )

            estado = (
                "completado"
                if not errores
                else "completado_con_observaciones"
            )

        except Exception as error:
            estado = "error"
            errores.append(str(error))
            respuesta = (
                "No fue posible completar la solicitud.\n\n"
                f"Detalle: {error}"
            )

            self._registrar_error(
                operacion_id=operacion_id,
                error=error,
                solicitud=solicitud,
            )

        fin = time.time()

        resultado_final = ResultadoEjecucion(
            id=operacion_id,
            solicitud=solicitud,
            categoria=categoria,
            estado=estado,
            respuesta=str(respuesta),
            tareas=[
                self._serializar_tarea(tarea)
                for tarea in tareas
            ],
            errores=errores,
            agentes_utilizados=list(dict.fromkeys(agentes_utilizados)),
            modo_ejecucion=modo,
            inicio=inicio,
            fin=fin,
            metadatos={
                "sistema": self.nombre,
                "version": self.version,
            },
        )

        self._finalizar_operacion(resultado_final)

        if devolver_detalles:
            return resultado_final.como_dict()

        return resultado_final.respuesta

    def _preparar_operacion(
        self,
        operacion_id: str,
        solicitud: str,
        contexto_adicional: Dict[str, Any],
    ) -> None:

        self._workspace_guardar("operacion_id", operacion_id)
        self._workspace_guardar("solicitud", solicitud)
        self._workspace_guardar(
            "contexto_adicional",
            contexto_adicional,
        )

        self._guardar_contexto("ultima_solicitud", solicitud)
        self._guardar_contexto("operacion_id", operacion_id)

        if self.activar_memoria:
            self._llamar_compatible(
                self.memoria,
                (
                    "registrar_solicitud",
                    "guardar_solicitud",
                    "agregar_solicitud",
                ),
                solicitud,
                requerido=False,
            )

        self._registrar_evento(
            "procesamiento_iniciado",
            {
                "operacion_id": operacion_id,
                "solicitud": solicitud,
            },
        )

    def _analizar_solicitud(
        self,
        solicitud: str,
    ) -> Dict[str, Any]:

        resultado = self._llamar_compatible(
            self.analizador,
            (
                "analizar",
                "analizar_tarea",
                "clasificar",
                "procesar",
            ),
            solicitud,
            requerido=False,
        )

        if resultado is None:
            resultado = AnalizadorRespaldo().analizar(solicitud)

        if isinstance(resultado, str):
            resultado = {
                "categoria": resultado,
                "complejidad": "baja",
                "requiere_enjambre": False,
            }

        if not isinstance(resultado, Mapping):
            resultado = {
                "categoria": "general",
                "complejidad": "baja",
                "requiere_enjambre": False,
                "resultado_original": resultado,
            }

        analisis = dict(resultado)
        analisis.setdefault("categoria", "general")
        analisis.setdefault("complejidad", "baja")
        analisis.setdefault("requiere_enjambre", False)

        self._workspace_guardar("analisis", analisis)

        return analisis

    def _construir_contexto(
        self,
        solicitud: str,
        analisis: Dict[str, Any],
        contexto_adicional: Dict[str, Any],
    ) -> Dict[str, Any]:

        contexto: Dict[str, Any] = {
            "solicitud": solicitud,
            "analisis": analisis,
            "workspace": self._workspace_snapshot(),
        }

        memoria_relevante = self._obtener_memoria_relevante(solicitud)

        if memoria_relevante is not None:
            contexto["memoria"] = memoria_relevante

        conocimiento = self._obtener_conocimiento_relevante(solicitud)

        if conocimiento is not None:
            contexto["conocimiento"] = conocimiento

        contexto.update(contexto_adicional)

        contexto_construido = self._llamar_compatible(
            self.contexto,
            (
                "construir",
                "crear_contexto",
                "preparar",
                "obtener_contexto",
            ),
            solicitud,
            analisis=analisis,
            memoria=memoria_relevante,
            conocimiento=conocimiento,
            extras=contexto_adicional,
            requerido=False,
        )

        if isinstance(contexto_construido, Mapping):
            contexto.update(contexto_construido)

        self._workspace_guardar("contexto_global", contexto)

        return contexto

    def _obtener_memoria_relevante(
        self,
        solicitud: str,
    ) -> Any:

        if not self.activar_memoria:
            return None

        return self._llamar_compatible(
            self.memoria,
            (
                "buscar_relevante",
                "recuperar_contexto",
                "buscar",
                "consultar",
                "obtener_contexto",
            ),
            solicitud,
            requerido=False,
        )

    def _obtener_conocimiento_relevante(
        self,
        solicitud: str,
    ) -> Any:

        if self.conocimiento is None:
            return None

        return self._llamar_compatible(
            self.conocimiento,
            (
                "buscar",
                "consultar",
                "recuperar",
                "obtener_relevante",
            ),
            solicitud,
            requerido=False,
        )

    def _crear_plan(
        self,
        solicitud: str,
        analisis: Dict[str, Any],
        contexto: Dict[str, Any],
    ) -> Any:

        categoria = str(analisis.get("categoria", "general"))

        plan = self._llamar_compatible(
            self.planner,
            (
                "crear_plan",
                "planificar",
                "generar_plan",
                "crear",
            ),
            categoria,
            solicitud=solicitud,
            analisis=analisis,
            contexto=contexto,
            requerido=False,
        )

        if plan is None:
            plan = PlannerRespaldo().crear_plan(
                categoria=categoria,
                solicitud=solicitud,
                analisis=analisis,
            )

        self._workspace_guardar("plan", plan)

        return plan

    def _normalizar_plan(
        self,
        plan: Any,
        categoria_default: str,
        solicitud: str,
    ) -> List[TareaOrquestada]:

        if plan is None:
            plan = [solicitud]

        if isinstance(plan, Mapping):
            plan = (
                plan.get("tareas")
                or plan.get("pasos")
                or plan.get("plan")
                or [plan]
            )

        if isinstance(plan, str):
            plan = [plan]

        if not isinstance(plan, Iterable):
            plan = [plan]

        tareas = [
            TareaOrquestada.desde_objeto(
                dato=tarea,
                indice=indice,
                categoria_default=categoria_default,
            )
            for indice, tarea in enumerate(plan)
        ]

        if not tareas:
            tareas = [
                TareaOrquestada(
                    id="tarea_1",
                    nombre="Procesamiento principal",
                    descripcion=solicitud,
                    categoria=categoria_default,
                    especialidad=categoria_default,
                    prioridad=1,
                )
            ]

        return sorted(
            tareas,
            key=lambda tarea: tarea.prioridad,
        )

    def _requiere_enjambre(
        self,
        analisis: Dict[str, Any],
        tareas: Sequence[TareaOrquestada],
    ) -> bool:

        if not self.activar_enjambre:
            return False

        indicado = bool(
            analisis.get("requiere_enjambre")
            or analisis.get("usar_enjambre")
            or analisis.get("enjambre")
        )

        complejidad = str(
            analisis.get("complejidad", "")
        ).lower()

        return (
            indicado
            or complejidad in {"alta", "critica", "crítica"}
            or len(tareas) > 1
        )

    def _ejecutar_plan(
        self,
        tareas: List[TareaOrquestada],
        contexto_global: Dict[str, Any],
        agente_preferido: Optional[str],
        agentes_utilizados: List[str],
        errores: List[str],
    ) -> List[Any]:

        resultados: List[Any] = []
        completadas: Dict[str, TareaOrquestada] = {}
        pendientes = list(tareas)

        while pendientes:
            ejecutables = [
                tarea
                for tarea in pendientes
                if all(
                    dependencia in completadas
                    for dependencia in tarea.dependencias
                )
            ]

            if not ejecutables:
                bloqueadas = ", ".join(
                    tarea.nombre
                    for tarea in pendientes
                )

                error = (
                    "El plan contiene dependencias no resueltas "
                    f"o circulares: {bloqueadas}"
                )

                errores.append(error)

                for tarea in pendientes:
                    tarea.estado = "bloqueada"
                    tarea.error = error

                break

            if len(ejecutables) == 1:
                tarea = ejecutables[0]

                resultado = self._ejecutar_tarea(
                    tarea=tarea,
                    contexto_global=contexto_global,
                    agente_preferido=agente_preferido,
                    agentes_utilizados=agentes_utilizados,
                )

                resultados.append(resultado)
                completadas[tarea.id] = tarea
                pendientes.remove(tarea)

                if tarea.error:
                    errores.append(tarea.error)

                continue

            with ThreadPoolExecutor(
                max_workers=min(
                    self.max_workers,
                    len(ejecutables),
                )
            ) as executor:

                futuros = {
                    executor.submit(
                        self._ejecutar_tarea,
                        tarea,
                        contexto_global,
                        agente_preferido,
                        agentes_utilizados,
                    ): tarea
                    for tarea in ejecutables
                }

                for futuro in as_completed(futuros):
                    tarea = futuros[futuro]

                    try:
                        resultado = futuro.result()
                    except Exception as error:
                        resultado = None
                        tarea.estado = "error"
                        tarea.error = str(error)

                    resultados.append(resultado)
                    completadas[tarea.id] = tarea
                    pendientes.remove(tarea)

                    if tarea.error:
                        errores.append(tarea.error)

        return resultados

    def _ejecutar_enjambre(
        self,
        tareas: List[TareaOrquestada],
        contexto_global: Dict[str, Any],
        agente_preferido: Optional[str],
        agentes_utilizados: List[str],
        errores: List[str],
    ) -> List[Any]:

        agentes = self.listar_agentes()

        if self.enjambre is not None:
            resultado = self._llamar_compatible(
                self.enjambre,
                (
                    "ejecutar",
                    "procesar",
                    "coordinar",
                    "ejecutar_enjambre",
                ),
                tareas,
                agentes=agentes,
                contexto=contexto_global,
                workspace=self.workspace,
                requerido=False,
            )

            if resultado is not None:
                if isinstance(resultado, Mapping):
                    resultados = (
                        resultado.get("resultados")
                        or resultado.get("respuestas")
                        or [resultado]
                    )
                elif isinstance(resultado, Sequence) and not isinstance(
                    resultado,
                    (str, bytes),
                ):
                    resultados = list(resultado)
                else:
                    resultados = [resultado]

                for agente in agentes:
                    agentes_utilizados.append(
                        self._nombre_agente(agente)
                    )

                return resultados

        return self._ejecutar_plan(
            tareas=tareas,
            contexto_global=contexto_global,
            agente_preferido=agente_preferido,
            agentes_utilizados=agentes_utilizados,
            errores=errores,
        )

    def _ejecutar_tarea(
        self,
        tarea: TareaOrquestada,
        contexto_global: Dict[str, Any],
        agente_preferido: Optional[str],
        agentes_utilizados: List[str],
    ) -> Any:

        tarea.estado = "seleccionando_agente"

        agente = self._seleccionar_agente(
            tarea=tarea,
            agente_preferido=agente_preferido,
        )

        if agente is None:
            mensaje = (
                "No se encontró un agente compatible para "
                f"la tarea '{tarea.nombre}' "
                f"con especialidad '{tarea.especialidad}'."
            )

            tarea.estado = "error"
            tarea.error = mensaje
            raise ErrorSeleccionAgente(mensaje)

        nombre_agente = self._nombre_agente(agente)
        tarea.agente = nombre_agente
        agentes_utilizados.append(nombre_agente)

        contexto_tarea = dict(contexto_global)
        contexto_tarea.update(tarea.contexto)

        contexto_tarea["tarea"] = {
            "id": tarea.id,
            "nombre": tarea.nombre,
            "descripcion": tarea.descripcion,
            "categoria": tarea.categoria,
            "especialidad": tarea.especialidad,
            "dependencias": tarea.dependencias,
            "metadatos": tarea.metadatos,
        }

        ultimo_error: Optional[Exception] = None

        for intento in range(1, self.max_reintentos + 2):
            tarea.intentos = intento
            tarea.estado = "ejecutando"

            try:
                resultado = self._invocar_agente(
                    agente=agente,
                    tarea=tarea,
                    contexto=contexto_tarea,
                )

                if resultado is None:
                    raise ErrorEjecucionAgente(
                        f"El agente {nombre_agente} devolvió "
                        "un resultado vacío."
                    )

                tarea.resultado = resultado
                tarea.estado = "completada"
                tarea.error = None

                self._workspace_guardar(
                    f"resultado.{tarea.id}",
                    resultado,
                )

                self._registrar_evento(
                    "tarea_completada",
                    {
                        "tarea": tarea.id,
                        "agente": nombre_agente,
                        "intentos": intento,
                    },
                )

                return resultado

            except Exception as error:
                ultimo_error = error
                tarea.estado = "reintentando"
                tarea.error = str(error)

                self._registrar_evento(
                    "error_tarea",
                    {
                        "tarea": tarea.id,
                        "agente": nombre_agente,
                        "intento": intento,
                        "error": str(error),
                    },
                )

        tarea.estado = "error"

        raise ErrorEjecucionAgente(
            f"El agente {nombre_agente} no pudo completar "
            f"'{tarea.nombre}': {ultimo_error}"
        )

    def _seleccionar_agente(
        self,
        tarea: TareaOrquestada,
        agente_preferido: Optional[str] = None,
    ) -> Optional[Any]:

        if agente_preferido:
            agente = self._obtener_agente_por_tag(
                agente_preferido
            )

            if agente is not None:
                return agente

        compatibles = self._buscar_agentes_compatibles(
            tarea.especialidad
        )

        if not compatibles and tarea.categoria != tarea.especialidad:
            compatibles = self._buscar_agentes_compatibles(
                tarea.categoria
            )

        if not compatibles:
            compatibles = self._buscar_agentes_compatibles(
                "general"
            )

        if not compatibles:
            agentes = self.listar_agentes()
            return agentes[0] if agentes else None

        return max(
            compatibles,
            key=lambda agente: self._puntuar_agente(
                agente,
                tarea,
            ),
        )

    def _buscar_agentes_compatibles(
        self,
        especialidad: str,
    ) -> List[Any]:

        resultado = self._llamar_compatible(
            self.registro,
            (
                "buscar_compatibles",
                "buscar_por_especialidad",
                "seleccionar_compatibles",
                "obtener_compatibles",
            ),
            especialidad,
            requerido=False,
        )

        if resultado is not None:
            if isinstance(resultado, Mapping):
                return list(resultado.values())

            if isinstance(resultado, Sequence) and not isinstance(
                resultado,
                (str, bytes),
            ):
                return list(resultado)

            return [resultado]

        compatibles = []

        for agente in self.listar_agentes():
            tag = str(
                getattr(
                    agente,
                    "INTENT_TAG",
                    getattr(agente, "intent_tag", "general"),
                )
            )

            especialidades = getattr(
                agente,
                "SPECIALTIES",
                getattr(agente, "especialidades", []),
            )

            if isinstance(especialidades, str):
                especialidades = [especialidades]

            if especialidad == tag or especialidad in especialidades:
                compatibles.append(agente)

        return compatibles

    def _obtener_agente_por_tag(
        self,
        tag: str,
    ) -> Optional[Any]:

        return self._llamar_compatible(
            self.registro,
            (
                "obtener",
                "buscar",
                "obtener_agente",
                "buscar_por_tag",
            ),
            tag,
            requerido=False,
        )

    @staticmethod
    def _puntuar_agente(
        agente: Any,
        tarea: TareaOrquestada,
    ) -> float:

        puntuacion = 0.0

        tag = str(
            getattr(
                agente,
                "INTENT_TAG",
                getattr(agente, "intent_tag", "general"),
            )
        )

        especialidades = getattr(
            agente,
            "SPECIALTIES",
            getattr(agente, "especialidades", []),
        )

        if isinstance(especialidades, str):
            especialidades = [especialidades]

        if tag == tarea.especialidad:
            puntuacion += 100.0

        if tarea.especialidad in especialidades:
            puntuacion += 80.0

        if tag == tarea.categoria:
            puntuacion += 50.0

        nivel = getattr(
            agente,
            "AGENT_LEVEL",
            getattr(agente, "nivel", 1),
        )

        try:
            puntuacion += float(nivel) * 5.0
        except (TypeError, ValueError):
            pass

        carga = getattr(
            agente,
            "carga_actual",
            getattr(agente, "carga", 0),
        )

        try:
            puntuacion -= float(carga)
        except (TypeError, ValueError):
            pass

        disponible = getattr(agente, "disponible", True)

        if not disponible:
            puntuacion -= 1000.0

        return puntuacion

    def _invocar_agente(
        self,
        agente: Any,
        tarea: TareaOrquestada,
        contexto: Dict[str, Any],
    ) -> Any:

        # Métodos exigidos: ejecutar, procesar, resolver, run
        metodos = (
            "ejecutar",
            "procesar",
            "resolver",
            "run",
        )

        for nombre_metodo in metodos:
            metodo = getattr(agente, nombre_metodo, None)

            if not callable(metodo):
                continue

            return self._invocar_funcion_flexible(
                metodo,
                tarea.descripcion,
                contexto_global=contexto,
                contexto=contexto,
                tarea=tarea,
            )

        if callable(agente):
            return self._invocar_funcion_flexible(
                agente,
                tarea.descripcion,
                contexto_global=contexto,
                contexto=contexto,
                tarea=tarea,
            )

        raise ErrorEjecucionAgente(
            f"El agente {self._nombre_agente(agente)} no expone "
            "un método ejecutar, procesar, resolver o run."
        )

    def _supervisar(
        self,
        solicitud: str,
        analisis: Dict[str, Any],
        tareas: List[TareaOrquestada],
        resultados: List[Any],
        contexto: Dict[str, Any],
    ) -> Any:

        if not self.activar_supervision or self.supervisor is None:
            return None

        reporte = self._llamar_compatible(
            self.supervisor,
            (
                "supervisar",
                "auditar",
                "revisar",
                "validar",
            ),
            resultados,
            solicitud=solicitud,
            analisis=analisis,
            tareas=tareas,
            contexto=contexto,
            workspace=self.workspace,
            requerido=False,
        )

        if reporte is not None:
            self._workspace_guardar(
                "reporte_supervision",
                reporte,
            )

        return reporte

    def _integrar(
        self,
        solicitud: str,
        analisis: Dict[str, Any],
        tareas: List[TareaOrquestada],
        resultados: List[Any],
        supervision: Any,
        contexto: Dict[str, Any],
    ) -> str:

        respuesta = self._llamar_compatible(
            self.integrador,
            (
                "integrar",
                "compilar",
                "consolidar",
                "generar_respuesta",
            ),
            resultados,
            solicitud=solicitud,
            analisis=analisis,
            tareas=tareas,
            supervision=supervision,
            contexto=contexto,
            requerido=False,
        )

        if respuesta is None:
            respuesta = IntegradorRespaldo().integrar(
                resultados=resultados,
            )

        if isinstance(respuesta, Mapping):
            respuesta = (
                respuesta.get("respuesta")
                or respuesta.get("resultado")
                or respuesta.get("contenido")
                or str(respuesta)
            )

        respuesta = str(respuesta).strip()

        if not respuesta:
            respuesta = (
                "La operación terminó, pero no produjo "
                "una respuesta textual."
            )

        self._workspace_guardar("respuesta_final", respuesta)

        return respuesta

    def _finalizar_operacion(
        self,
        resultado: ResultadoEjecucion,
    ) -> None:

        resultado_dict = resultado.como_dict()

        self._workspace_guardar(
            "ultimo_resultado",
            resultado_dict,
        )

        if self.activar_memoria:
            registrado = self._llamar_compatible(
                self.memoria,
                (
                    "registrar_resultado",
                    "guardar_resultado",
                    "agregar_resultado",
                ),
                resultado_dict,
                requerido=False,
            )

            if registrado is None:
                self._memoria_guardar(
                    "ultimo_resultado",
                    resultado_dict,
                )

        self._registrar_evento(
            "procesamiento_finalizado",
            {
                "operacion_id": resultado.id,
                "estado": resultado.estado,
                "duracion": resultado.duracion,
            },
        )

    def _registrar_error(
        self,
        operacion_id: str,
        error: Exception,
        solicitud: str,
    ) -> None:

        registro = {
            "operacion_id": operacion_id,
            "solicitud": solicitud,
            "tipo": error.__class__.__name__,
            "error": str(error),
            "timestamp": time.time(),
        }

        self._llamar_compatible(
            self.memoria,
            (
                "registrar_error",
                "guardar_error",
                "agregar_error",
            ),
            registro,
            requerido=False,
        )

        self._workspace_guardar("ultimo_error", registro)
        self.logger.exception(error)

    def _workspace_guardar(
        self,
        clave: str,
        valor: Any,
    ) -> None:

        self._llamar_compatible(
            self.workspace,
            (
                "guardar",
                "actualizar",
                "set",
            ),
            clave,
            valor,
            requerido=False,
        )

    def _workspace_snapshot(self) -> Dict[str, Any]:
        posibles = (
            "workspace",
            "datos",
            "data",
        )

        for atributo in posibles:
            valor = getattr(self.workspace, atributo, None)

            if isinstance(valor, Mapping):
                return dict(valor)

        resultado = self._llamar_compatible(
            self.workspace,
            (
                "obtener_todo",
                "exportar",
                "snapshot",
                "como_dict",
            ),
            requerido=False,
        )

        if isinstance(resultado, Mapping):
            return dict(resultado)

        return {}

    def _memoria_guardar(
        self,
        clave: str,
        valor: Any,
    ) -> None:

        self._llamar_compatible(
            self.memoria,
            (
                "guardar",
                "save",
                "establecer",
            ),
            clave,
            valor,
            requerido=False,
        )

    def _guardar_contexto(
        self,
        clave: str,
        valor: Any,
    ) -> None:

        self._llamar_compatible(
            self.contexto,
            (
                "guardar",
                "actualizar",
                "set",
            ),
            clave,
            valor,
            requerido=False,
        )

    def _llamar_compatible(
        self,
        objeto: Any,
        nombres: Sequence[str],
        *args: Any,
        requerido: bool = False,
        **kwargs: Any,
    ) -> Any:

        if objeto is None:
            if requerido:
                raise ErrorConfiguracion(
                    f"No existe el componente requerido: {nombres[0]}"
                )
            return None

        ultimo_error: Optional[Exception] = None

        for nombre in nombres:
            funcion = getattr(objeto, nombre, None)

            if not callable(funcion):
                continue

            try:
                return self._invocar_funcion_flexible(
                    funcion,
                    *args,
                    **kwargs,
                )
            except TypeError as error:
                ultimo_error = error
                continue

        if requerido:
            detalle = (
                f" Último error: {ultimo_error}"
                if ultimo_error
                else ""
            )

            raise ErrorConfiguracion(
                f"{objeto.__class__.__name__} no expone un método "
                f"compatible entre {tuple(nombres)}.{detalle}"
            )

        return None

    @staticmethod
    def _invocar_funcion_flexible(
        funcion: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        try:
            firma = inspect.signature(funcion)
        except (TypeError, ValueError):
            return funcion(*args, **kwargs)

        parametros = firma.parameters

        acepta_kwargs = any(
            parametro.kind == inspect.Parameter.VAR_KEYWORD
            for parametro in parametros.values()
        )

        if acepta_kwargs:
            kwargs_filtrados = kwargs
        else:
            kwargs_filtrados = {
                clave: valor
                for clave, valor in kwargs.items()
                if clave in parametros
            }

        try:
            return funcion(*args, **kwargs_filtrados)
        except TypeError:
            pass

        intentos = [
            lambda: funcion(*args),
            lambda: funcion(**kwargs_filtrados),
            lambda: funcion(args[0]) if args else funcion(),
            lambda: funcion(),
        ]

        ultimo_error: Optional[Exception] = None

        for intento in intentos:
            try:
                return intento()
            except TypeError as error:
                ultimo_error = error

        if ultimo_error:
            raise ultimo_error

        return None

    @staticmethod
    def _validar_solicitud(solicitud: Any) -> str:
        if solicitud is None:
            raise ValueError("La solicitud no puede ser nula.")

        solicitud = str(solicitud).strip()

        if not solicitud:
            raise ValueError("La solicitud no puede estar vacía.")

        return solicitud

    @staticmethod
    def _nombre_agente(agente: Any) -> str:
        return str(
            getattr(
                agente,
                "NOMBRE",
                getattr(
                    agente,
                    "nombre",
                    getattr(
                        agente,
                        "INTENT_TAG",
                        agente.__class__.__name__,
                    ),
                ),
            )
        )

    @staticmethod
    def _serializar_tarea(
        tarea: TareaOrquestada,
    ) -> Dict[str, Any]:

        return {
            "id": tarea.id,
            "nombre": tarea.nombre,
            "descripcion": tarea.descripcion,
            "categoria": tarea.categoria,
            "especialidad": tarea.especialidad,
            "prioridad": tarea.prioridad,
            "dependencias": tarea.dependencias,
            "estado": tarea.estado,
            "agente": tarea.agente,
            "resultado": tarea.resultado,
            "error": tarea.error,
            "intentos": tarea.intentos,
            "metadatos": tarea.metadatos,
        }

    def _registrar_evento(
        self,
        tipo: str,
        datos: Dict[str, Any],
    ) -> None:

        evento = {
            "tipo": tipo,
            "timestamp": time.time(),
            "datos": datos,
        }

        with self._lock:
            self._historial_operaciones.append(evento)

        self.logger.info("%s: %s", tipo, datos)

    def obtener_estado(self) -> Dict[str, Any]:
        return {
            "sistema": self.nombre,
            "version": self.version,
            "agentes_registrados": [
                self._nombre_agente(agente)
                for agente in self.listar_agentes()
            ],
            "componentes": {
                "memoria": self.memoria is not None,
                "workspace": self.workspace is not None,
                "registro": self.registro is not None,
                "contexto": self.contexto is not None,
                "conocimiento": self.conocimiento is not None,
                "analizador": self.analizador is not None,
                "planner": self.planner is not None,
                "enjambre": self.enjambre is not None,
                "supervisor": self.supervisor is not None,
                "integrador": self.integrador is not None,
            },
            "eventos_registrados": len(
                self._historial_operaciones
            ),
        }

    def obtener_historial(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._historial_operaciones)

    def limpiar_workspace(self) -> None:
        self._llamar_compatible(
            self.workspace,
            (
                "limpiar",
                "clear",
                "reiniciar",
            ),
            requerido=False,
        )


# ==========================================================
# ALIAS DE COMPATIBILIDAD
# ==========================================================

ScalableSwarmOrchestrator = Orquestador
Orchestrator = Orquestador


# ==========================================================
# PRUEBA LOCAL DE VALIDACIÓN
# ==========================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    orquestador = Orquestador()

    print("Estado inicial:")
    print(orquestador.obtener_estado())

    print("\nPrueba de ejecución con orquestador.procesar():")
    print(
        orquestador.procesar(
            "Verifica la compatibilidad de los submódulos de DraymSystem IA."
        )
    )
