"""Conexão SQLite compartilhada entre a API Node/Prisma e a GUI Python.

Reaproveita o arquivo ``prisma/dev.db`` já criado pelo Prisma, com as
mesmas tabelas (``Veiculo`` e ``Manutencao``), para não duplicar dados.
Permite sobrepor o caminho com a variável de ambiente ``CAR_DB_PATH``
(útil para testes).
"""

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("CAR_DB_PATH", BASE_DIR / "prisma" / "dev.db"))


def get_connection(db_path=None):
    """Retorna uma conexão SQLite com chaves estrangeiras ativadas."""
    path = Path(db_path) if db_path else DB_PATH
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn=None):
    """Cria as tabelas caso ainda não existam (mesmo schema do Prisma)."""
    propria = conn is None
    conn = conn or get_connection()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS "Veiculo" (
                    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "placa" TEXT NOT NULL,
                    "modelo" TEXT NOT NULL,
                    "marca" TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS "Manutencao" (
                    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "descricao" TEXT NOT NULL,
                    "data" TEXT NOT NULL,
                    "valor" REAL NOT NULL,
                    "veiculoId" INTEGER NOT NULL,
                    CONSTRAINT "Manutencao_veiculoId_fkey"
                        FOREIGN KEY ("veiculoId") REFERENCES "Veiculo" ("id")
                        ON DELETE RESTRICT ON UPDATE CASCADE
                )
                """
            )
            conn.execute(
                'CREATE UNIQUE INDEX IF NOT EXISTS "Veiculo_placa_key" '
                'ON "Veiculo"("placa")'
            )
    finally:
        if propria:
            conn.close()
    return conn
