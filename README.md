# DraymSystem IA

Sistema multiagente en Python (orquestador + agentes especializados). Funciona en local sin claves ni servicios externos.

## Estructura

```
main.py            # punto de entrada (consola / GUI / verificación)
core/              # orquestador, configuracion, memoria, workspace, registro_agentes,
                   # enjambre, supervisor, integrador, scheduler, selector_agentes
motor_ia/          # contexto, conocimiento, analizador_tareas, planner, nlp,
                   # tokenizador, razonamiento, matematicas
agentes/           # base_agente + agente_{general,analista,arquitecto,codigo,
                   # documentacion,investigador,qa}
interfaz/          # app_kivy.py (interfaz gráfica opcional)
```

## Requisitos

- Python 3.9+
- Modo consola: sin dependencias externas.
- Interfaz gráfica (opcional): `pip install kivy`

## Ejecución

```bash
python main.py                  # chat interactivo en consola
python main.py "tu solicitud"   # una sola consulta
python main.py --gui            # interfaz Kivy
```

Los datos de ejecución se guardan en `datos/` (ignorado por git).

## Verificación rápida

```bash
python -m compileall -q . && python main.py --check
```
