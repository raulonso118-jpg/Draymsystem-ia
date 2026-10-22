"""Agentes especializados de DraymSystem IA."""


def crear_agentes():
    """Instancia todos los agentes disponibles."""
    from agentes.agente_analista import AgenteAnalista
    from agentes.agente_arquitecto import AgenteArquitecto
    from agentes.agente_codigo import AgenteCodigo
    from agentes.agente_documentacion import AgenteDocumentacion
    from agentes.agente_general import AgenteGeneral
    from agentes.agente_investigador import AgenteInvestigador
    from agentes.agente_qa import AgenteQA

    return [
        AgenteGeneral(),
        AgenteAnalista(),
        AgenteArquitecto(),
        AgenteCodigo(),
        AgenteDocumentacion(),
        AgenteInvestigador(),
        AgenteQA(),
    ]
