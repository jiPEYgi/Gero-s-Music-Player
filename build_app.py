"""Build script for Gero's Music Player using PyInstaller.

Bundles all assets, CustomTkinter dependencies, and metadata libraries
into a standalone executable without compilation or packaging errors.
"""

import subprocess
import sys
from pathlib import Path


def build():
    project_root = Path(__file__).resolve().parent
    main_script = project_root / "main.py"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name",
        "GerosMusicPlayer",
        "--collect-all",
        "customtkinter",
        "--copy-metadata",
        "customtkinter",
        "--copy-metadata",
        "mutagen",
        "--copy-metadata",
        "pillow",
        str(main_script),
    ]

    print("Ejecutando build con PyInstaller...")
    print("Comando:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode == 0:
        print("\n¡Build completado con éxito! El ejecutable se encuentra en dist/GerosMusicPlayer/")
    else:
        print(f"\nEl build falló con código de error {result.returncode}.", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
