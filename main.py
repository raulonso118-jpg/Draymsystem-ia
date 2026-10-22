"""Punto de entrada de DraymSystem IA.

Uso:
    python main.py                 # chat en consola (sin dependencias externas)
    python main.py "tu solicitud"  # una sola consulta
    python main.py --gui           # interfaz Kivy (requiere `pip install kivy`)
    python main.py --check         # verificación rápida de importaciones
"""

import sys


def crear_orquestador():
    from core.orquestador import Orquestador
    from agentes import crear_agentes

    orquestador = Orquestador()
    orquestador.registrar_agentes(crear_agentes())
    return orquestador


def verificar():
    import glob
    import importlib

    errores = 0
    for ruta in sorted(glob.glob("*/*.py")):
        if ruta.endswith("__init__.py") or ruta.startswith("interfaz/"):
            continue
        modulo = ruta[:-3].replace("/", ".")
        try:
            importlib.import_module(modulo)
        except Exception as e:
            errores += 1
            print(f"ERROR importando {modulo}: {e}")
    orquestador = crear_orquestador()
    print(orquestador.obtener_estado())
    print("OK" if not errores else f"{errores} errores")
    return 1 if errores else 0


def main(argv):
    if "--check" in argv:
        return verificar()

    if "--gui" in argv:
        try:
            from interfaz.app_kivy import DraymSystemApp
        except ImportError as e:
            print(f"No se pudo cargar la interfaz Kivy ({e}). Instala con: pip install kivy")
            return 1
        DraymSystemApp().run()
        return 0

    orquestador = crear_orquestador()
    consulta = " ".join(a for a in argv if not a.startswith("--"))
    if consulta:
        print(orquestador.procesar(consulta))
        return 0

    print("DraymSystem IA - escribe 'salir' para terminar.")
    while True:
        try:
            texto = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if texto.lower() in ("salir", "exit", "quit"):
            return 0
        if texto:
            print(orquestador.procesar(texto))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
