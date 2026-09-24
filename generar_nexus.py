#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "NEXUS_FORENSIC_CONTEXT.md"


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Directorios completamente ignorados
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}


# Archivos específicos que nunca deben entrar
EXCLUDED_FILES = {
    ".env",
    "nexus.db",
    "backend/nexus.db",
    "nexus_backend_fase1.zip",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "NEXUS_FORENSIC_CONTEXT.md",
}


# Extensiones permitidas
ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".css",
    ".scss",
    ".html",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
    ".md",
}


# Archivos pequeños de configuración sin extensión relevante
ALLOWED_FILENAMES = {
    "Dockerfile",
    "Makefile",
    "requirements.txt",
}


# Archivos visuales/binarios/documentación pesada
BLOCKED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}


# ============================================================
# VALIDACIÓN
# ============================================================

def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def should_exclude(path: Path) -> bool:
    rel = relative_path(path)

    # Directorios ignorados
    for part in path.relative_to(ROOT).parts:
        if part in EXCLUDED_DIRS:
            return True

    # Archivos explícitos
    if rel in EXCLUDED_FILES:
        return True

    # Extensiones bloqueadas
    if path.suffix.lower() in BLOCKED_EXTENSIONS:
        return True

    # Solo extensiones permitidas
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        if path.name not in ALLOWED_FILENAMES:
            return True

    # Nunca incluir el propio archivo generado
    if path.resolve() == OUTPUT.resolve():
        return True

    return False


def is_probably_text(path: Path) -> bool:
    try:
        data = path.read_bytes()

        # Evita archivos extremadamente grandes
        if len(data) > 1_000_000:
            return False

        data.decode("utf-8")
        return True

    except (UnicodeDecodeError, OSError):
        return False


# ============================================================
# DESCUBRIR ARCHIVOS
# ============================================================

def collect_files():
    files = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if should_exclude(path):
            continue

        if not is_probably_text(path):
            continue

        files.append(path)

    return sorted(
        files,
        key=lambda p: (
            0 if relative_path(p).startswith("backend/app/") else
            1 if relative_path(p).startswith("frontend/src/") else
            2,
            relative_path(p)
        )
    )


# ============================================================
# TREE COMPACTO
# ============================================================

def build_tree(files):
    lines = ["```text"]

    directories = sorted(
        {
            str(path.parent.relative_to(ROOT))
            for path in files
        }
    )

    lines.append("NEXUS FORENSIC")

    for directory in directories:
        if directory != ".":
            lines.append(f"├── {directory}/")

    for path in files:
        rel = relative_path(path)
        lines.append(f"├── {rel}")

    lines.append("```")

    return "\n".join(lines)


# ============================================================
# GENERACIÓN
# ============================================================

def main():
    files = collect_files()

    sections = []

    sections.append(
        "# NEXUS FORENSIC — AI CONTEXT PACK\n\n"
        "Contexto técnico compacto del proyecto para asistentes de IA.\n\n"
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Archivos incluidos: {len(files)}\n"
    )

    sections.append(
        "\n## 1. ESTRUCTURA DEL PROYECTO\n\n"
        + build_tree(files)
    )

    sections.append(
        "\n## 2. ARCHIVOS DEL PROYECTO\n\n"
        "Cada archivo aparece una sola vez. "
        "Los binarios, bases de datos, dependencias instaladas, "
        "archivos sensibles y artefactos generados fueron excluidos.\n"
    )

    for path in files:
        rel = relative_path(path)

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="replace"
            ).strip()

        except OSError as exc:
            print(f"[WARN] No se pudo leer {rel}: {exc}")
            continue

        if not content:
            continue

        language = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".css": "css",
            ".scss": "scss",
            ".html": "html",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".md": "markdown",
            ".txt": "text",
            ".toml": "toml",
        }.get(path.suffix.lower(), "")

        sections.append(
            f"\n### FILE: `{rel}`\n\n"
            f"```{language}\n"
            f"{content}\n"
            "```\n"
        )

    final_content = "\n".join(sections)

    OUTPUT.write_text(
        final_content,
        encoding="utf-8"
    )

    size_bytes = OUTPUT.stat().st_size
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024

    print()
    print("=" * 60)
    print(" NEXUS FORENSIC — CONTEXT PACK")
    print("=" * 60)
    print(f"Archivos incluidos : {len(files)}")
    print(f"Tamaño              : {size_kb:,.2f} KB")
    print(f"Tamaño              : {size_mb:,.2f} MB")
    print(f"Salida              : {OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
