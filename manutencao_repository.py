"""Regras de negócio e persistência de Manutenções (camada de dados)."""

import sqlite3
from datetime import datetime

from database import get_connection
from veiculo_repository import VeiculoRepository


def _parse_valor(valor):
    if isinstance(valor, str):
        valor = valor.strip().replace(",", ".")
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        raise ValueError("Valor inválido. Informe um número (ex.: 250.00).") from None
    if valor < 0:
        raise ValueError("Valor não pode ser negativo.")
    return valor


def _validar(descricao, data, valor, veiculo_id):
    descricao = (descricao or "").strip()
    data = (data or "").strip()
    if not descricao or not data:
        raise ValueError("Descrição e data são obrigatórias.")
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Data inválida. Use o formato AAAA-MM-DD (ex.: 2026-11-18).") from None
    try:
        veiculo_id = int(veiculo_id)
    except (TypeError, ValueError):
        raise ValueError("Selecione um veículo válido (ID inválido).") from None
    return descricao, data, _parse_valor(valor), veiculo_id


class ManutencaoRepository:
    def __init__(self, conn=None):
        self._propria = conn is None
        self.conn = conn or get_connection()
        self.veiculos = VeiculoRepository(self.conn)

    def fechar(self):
        if self._propria:
            self.conn.close()

    def criar(self, descricao, data, valor, veiculo_id):
        descricao, data, valor, veiculo_id = _validar(descricao, data, valor, veiculo_id)
        self.veiculos.buscar_por_id(veiculo_id)  # garante ID válido (FK)
        try:
            with self.conn:
                cur = self.conn.execute(
                    'INSERT INTO "Manutencao" (descricao, data, valor, "veiculoId") '
                    "VALUES (?, ?, ?, ?)",
                    (descricao, data, valor, veiculo_id),
                )
        except sqlite3.IntegrityError:
            raise ValueError("Veículo não encontrado. Verifique o ID selecionado.") from None
        return self.buscar_por_id(cur.lastrowid)

    def listar(self):
        return self.conn.execute(
            'SELECT m.*, v.placa, v.modelo, v.marca FROM "Manutencao" m '
            'JOIN "Veiculo" v ON v.id = m."veiculoId" ORDER BY m.data DESC, m.id DESC'
        ).fetchall()

    def listar_por_veiculo(self, veiculo_id):
        self.veiculos.buscar_por_id(veiculo_id)
        return self.conn.execute(
            'SELECT m.*, v.placa, v.modelo, v.marca FROM "Manutencao" m '
            'JOIN "Veiculo" v ON v.id = m."veiculoId" '
            'WHERE m."veiculoId" = ? ORDER BY m.data DESC, m.id DESC',
            (int(veiculo_id),),
        ).fetchall()

    def buscar_por_id(self, manutencao_id):
        try:
            manutencao_id = int(manutencao_id)
        except (TypeError, ValueError):
            raise ValueError("ID da manutenção inválido.") from None
        row = self.conn.execute(
            'SELECT m.*, v.placa, v.modelo, v.marca FROM "Manutencao" m '
            'JOIN "Veiculo" v ON v.id = m."veiculoId" WHERE m.id = ?',
            (manutencao_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Manutenção com ID {manutencao_id} não encontrada.")
        return row

    def atualizar(self, manutencao_id, descricao, data, valor, veiculo_id=None):
        atual = self.buscar_por_id(manutencao_id)
        if veiculo_id is None:
            veiculo_id = atual["veiculoId"]
        descricao, data, valor, veiculo_id = _validar(descricao, data, valor, veiculo_id)
        self.veiculos.buscar_por_id(veiculo_id)
        with self.conn:
            self.conn.execute(
                'UPDATE "Manutencao" SET descricao = ?, data = ?, valor = ?, '
                '"veiculoId" = ? WHERE id = ?',
                (descricao, data, valor, veiculo_id, int(manutencao_id)),
            )
        return self.buscar_por_id(manutencao_id)

    def excluir(self, manutencao_id):
        self.buscar_por_id(manutencao_id)
        with self.conn:
            self.conn.execute(
                'DELETE FROM "Manutencao" WHERE id = ?', (int(manutencao_id),)
            )
