import hashlib
import os
from typing import BinaryIO


def calculate_sha256(file_obj: BinaryIO, chunk_size: int = 8192) -> str:
    """Calcula SHA-256 directamente de un objeto archivo (ej: UploadFile.file)"""
    sha256_hash = hashlib.sha256()
    file_obj.seek(0)
    for byte_block in iter(lambda: file_obj.read(chunk_size), b""):
        sha256_hash.update(byte_block)
    file_obj.seek(0)  # Devolver el puntero al inicio para guardado posterior
    return sha256_hash.hexdigest()


def calculate_sha256_from_path(file_path: str, chunk_size: int = 8192) -> str:
    """Calcula SHA-256 leyendo desde el sistema de archivos local"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as f:
        return calculate_sha256(f, chunk_size)
