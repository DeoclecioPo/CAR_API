"""Regras de negócio e persistência de Veículos (camada de dados)."""

import re
import sqlite3

from database import get_connection

_PLACA_RE = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")


def _validar(placa, modelo, marca):
    placa = (placa or "").strip().upper().replace("-", "").replace(" ", "")
    modelo = (modelo or "").strip()
    marca = (marca or "").strip()
    if not placa or not modelo or not marca:
        raise ValueError("Preencha todos os campos: placa, modelo e marca são obrigatórios.")
    if not _PLACA_RE.match(placa):
        raise ValueError("Placa inválida. Use o formato Mercosul (ex.: ABC1D23) ou antigo (ABC1234).")
    return placa, modelo, marca


class VeiculoRepository:
    def __init__(self, conn=None):
        self._propria = conn is None
        self.conn = conn or get_connection()

    def fechar(self):
        if self._propria:
            self.conn.close()

    def criar(self, placa, modelo, marca):
        placa, modelo, marca = _validar(placa, modelo, marca)
        try:
            with self.conn:
                cur = self.conn.execute(
                    'INSERT INTO "Veiculo" (placa, modelo, marca) VALUES (?, ?, ?)',
                    (placa, modelo, marca),
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"A placa {placa} já está cadastrada.") from None
        return self.buscar_por_id(cur.lastrowid)

    def listar(self):
        return self.conn.execute(
            'SELECT v.*, COUNT(m.id) AS total_manutencoes FROM "Veiculo" v '
            'LEFT JOIN "Manutencao" m ON m."veiculoId" = v.id '
            "GROUP BY v.id ORDER BY v.id"
        ).fetchall()

    def buscar_por_id(self, veiculo_id):
        try:
            veiculo_id = int(veiculo_id)
        except (TypeError, ValueError):
            raise ValueError("ID do veículo inválido.") from None
        row = self.conn.execute(
            'SELECT * FROM "Veiculo" WHERE id = ?', (veiculo_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Veículo com ID {veiculo_id} não encontrado.")
        return row

    def atualizar(self, veiculo_id, placa, modelo, marca):
        placa, modelo, marca = _validar(placa, modelo, marca)
        self.buscar_por_id(veiculo_id)
        try:
            with self.conn:
                self.conn.execute(
                    'UPDATE "Veiculo" SET placa = ?, modelo = ?, marca = ? WHERE id = ?',
                    (placa, modelo, marca, int(veiculo_id)),
                )
        except sqlite3.IntegrityError:
            raise ValueError(f"A placa {placa} já está cadastrada.") from None
        return self.buscar_por_id(veiculo_id)

    def excluir(self, veiculo_id):
        self.buscar_por_id(veiculo_id)
        total = self.conn.execute(
            'SELECT COUNT(*) FROM "Manutencao" WHERE "veiculoId" = ?',
            (int(veiculo_id),),
        ).fetchone()[0]
        if total:
            raise ValueError(
                f"Este veículo possui {total} manutenção(ões) e não pode ser excluído. "
                "Exclua ou transfira as manutenções primeiro."
            )
        with self.conn:
            self.conn.execute('DELETE FROM "Veiculo" WHERE id = ?', (int(veiculo_id),))
