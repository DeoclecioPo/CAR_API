"""Sistema de Controle de Veículos e Histórico de Manutenções (Tkinter).

Interface Desktop que usa a mesma base SQLite (``prisma/dev.db``) da API
Node/Prisma. Relacionamento 1:N: um Veículo possui várias Manutenções.

Execute:  python app.py
"""

import tkinter as tk
from tkinter import messagebox, ttk

from database import init_db
from manutencao_repository import ManutencaoRepository
from veiculo_repository import VeiculoRepository


def _erro(exc):
    messagebox.showerror("Erro", str(exc))


class VeiculosFrame(ttk.Frame):
    def __init__(self, master, repo, on_change=None):
        super().__init__(master, padding=10)
        self.repo = repo
        self.on_change = on_change or (lambda: None)
        self._build()
        self.atualizar_tabela()

    def _build(self):
        ttk.Label(self, text="Veículos", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.tabela = ttk.Treeview(
            self, columns=("id", "placa", "modelo", "marca", "total"),
            show="headings", height=8)
        for col, titulo, larg in [
                ("id", "ID", 50), ("placa", "Placa", 100),
                ("modelo", "Modelo", 180), ("marca", "Marca", 160),
                ("total", "Manutenções", 100)]:
            self.tabela.heading(col, text=titulo)
            self.tabela.column(col, width=larg)
        self.tabela.pack(fill="both", expand=True, pady=8)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar)
        self.tabela.bind("<Double-1>", lambda _: self._editar())

        form = ttk.Frame(self)
        form.pack(fill="x")
        self.campos = {}
        for i, (nome, rotulo) in enumerate(
                [("placa", "Placa"), ("modelo", "Modelo"), ("marca", "Marca")]):
            ttk.Label(form, text=rotulo).grid(row=0, column=i * 2, sticky="w")
            var = tk.StringVar()
            ttk.Entry(form, textvariable=var, width=20).grid(
                row=0, column=i * 2 + 1, padx=4, sticky="w")
            self.campos[nome] = var

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", pady=8)
        ttk.Button(botoes, text="Cadastrar", command=self._criar).pack(side="left")
        ttk.Button(botoes, text="Editar/Salvar", command=self._editar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir", command=self._excluir).pack(side="left")
        ttk.Button(botoes, text="Limpar", command=self._limpar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Atualizar lista", command=self.atualizar_tabela).pack(side="left")

    def _selecionar(self, _=None):
        sel = self.tabela.selection()
        if not sel:
            return
        v = self.tabela.item(sel[0], "values")
        for nome, valor in zip(("placa", "modelo", "marca"), v[1:4]):
            self.campos[nome].set(valor)

    def _id_selecionado(self):
        sel = self.tabela.selection()
        if not sel:
            raise ValueError("Selecione um veículo na lista primeiro.")
        return int(self.tabela.item(sel[0], "values")[0])

    def _limpar(self):
        for var in self.campos.values():
            var.set("")
        self.tabela.selection_remove(self.tabela.selection())

    def _criar(self):
        try:
            self.repo.criar(self.campos["placa"].get(), self.campos["modelo"].get(),
                            self.campos["marca"].get())
        except Exception as exc:  # ValueError / sqlite3.Error amigável
            return _erro(exc)
        messagebox.showinfo("Sucesso", "Veículo cadastrado.")
        self._limpar(); self.atualizar_tabela(); self.on_change()

    def _editar(self):
        try:
            self.repo.atualizar(self._id_selecionado(), self.campos["placa"].get(),
                                self.campos["modelo"].get(), self.campos["marca"].get())
        except Exception as exc:
            return _erro(exc)
        messagebox.showinfo("Sucesso", "Veículo atualizado.")
        self._limpar(); self.atualizar_tabela(); self.on_change()

    def _excluir(self):
        try:
            vid = self._id_selecionado()
        except Exception as exc:
            return _erro(exc)
        if not messagebox.askyesno("Confirmar", f"Excluir o veículo ID {vid}?"):
            return
        try:
            self.repo.excluir(vid)
        except Exception as exc:
            return _erro(exc)
        messagebox.showinfo("Sucesso", "Veículo excluído.")
        self._limpar(); self.atualizar_tabela(); self.on_change()

    def atualizar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        try:
            for v in self.repo.listar():
                self.tabela.insert("", "end", values=(
                    v["id"], v["placa"], v["modelo"], v["marca"], v["total_manutencoes"]))
        except Exception as exc:
            _erro(exc)


class ManutencoesFrame(ttk.Frame):
    def __init__(self, master, repo, veiculos_repo):
        super().__init__(master, padding=10)
        self.repo = repo
        self.veiculos_repo = veiculos_repo
        self._build()
        self.atualizar_tabela()

    def _build(self):
        ttk.Label(self, text="Manutenções", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.tabela = ttk.Treeview(
            self, columns=("id", "descricao", "data", "valor", "veiculo"),
            show="headings", height=8)
        for col, titulo, larg in [
                ("id", "ID", 50), ("descricao", "Descrição", 240),
                ("data", "Data", 100), ("valor", "Valor (R$)", 90),
                ("veiculo", "Veículo", 220)]:
            self.tabela.heading(col, text=titulo)
            self.tabela.column(col, width=larg)
        self.tabela.pack(fill="both", expand=True, pady=8)
        self.tabela.bind("<<TreeviewSelect>>", self._selecionar)
        self.tabela.bind("<Double-1>", lambda _: self._editar())

        form = ttk.Frame(self)
        form.pack(fill="x")
        self.descricao = tk.StringVar()
        self.data = tk.StringVar()
        self.valor = tk.StringVar()
        self.veiculo = ttk.Combobox(form, state="readonly", width=34)
        for i, (rotulo, widget) in enumerate([
                ("Descrição", ttk.Entry(form, textvariable=self.descricao, width=24)),
                ("Data (AAAA-MM-DD)", ttk.Entry(form, textvariable=self.data, width=14)),
                ("Valor (R$)", ttk.Entry(form, textvariable=self.valor, width=12)),
                ("Veículo", self.veiculo)]):
            ttk.Label(form, text=rotulo).grid(row=0, column=i * 2, sticky="w")
            widget.grid(row=0, column=i * 2 + 1, padx=4, sticky="w")
        self._carregar_veiculos()

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", pady=8)
        ttk.Button(botoes, text="Cadastrar", command=self._criar).pack(side="left")
        ttk.Button(botoes, text="Editar/Salvar", command=self._editar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir", command=self._excluir).pack(side="left")
        ttk.Button(botoes, text="Limpar", command=self._limpar).pack(side="left", padx=4)
        ttk.Button(botoes, text="Atualizar lista", command=self.atualizar_tabela).pack(side="left")

    def _carregar_veiculos(self):
        try:
            self._veiculos = self.veiculos_repo.listar()
        except Exception:
            self._veiculos = []
        self.veiculo["values"] = [
            f'{v["id"]} - {v["placa"]} {v["marca"]} {v["modelo"]}' for v in self._veiculos]

    def _veiculo_id(self):
        texto = self.veiculo.get()
        if not texto:
            raise ValueError("Selecione um veículo.")
        try:
            return int(texto.split(" - ", 1)[0])
        except (ValueError, IndexError):
            raise ValueError("Veículo selecionado é inválido.") from None

    def _selecionar(self, _=None):
        sel = self.tabela.selection()
        if not sel:
            return
        m = self.tabela.item(sel[0], "values")
        self.descricao.set(m[1]); self.data.set(m[2]); self.valor.set(m[3])
        # A coluna "veiculo" exibe placa/modelo; busca o ID no repositório.
        for v in self._veiculos:
            if v["placa"] in str(m[4]):
                self.veiculo.set(
                    f'{v["id"]} - {v["placa"]} {v["marca"]} {v["modelo"]}')
                break

    def _id_selecionado(self):
        sel = self.tabela.selection()
        if not sel:
            raise ValueError("Selecione uma manutenção na lista primeiro.")
        return int(self.tabela.item(sel[0], "values")[0])

    def _limpar(self):
        for var in (self.descricao, self.data, self.valor):
            var.set("")
        self.veiculo.set("")
        self.tabela.selection_remove(self.tabela.selection())

    def _criar(self):
        try:
            self.repo.criar(self.descricao.get(), self.data.get(), self.valor.get(),
                            self._veiculo_id())
        except Exception as exc:
            return _erro(exc)
        messagebox.showinfo("Sucesso", "Manutenção cadastrada.")
        self._limpar(); self.atualizar_tabela()

    def _editar(self):
        try:
            self.repo.atualizar(self._id_selecionado(), self.descricao.get(),
                                self.data.get(), self.valor.get(), self._veiculo_id())
        except Exception as exc:
            return _erro(exc)
        messagebox.showinfo("Sucesso", "Manutenção atualizada.")
        self._limpar(); self.atualizar_tabela()

    def _excluir(self):
        try:
            mid = self._id_selecionado()
        except Exception as exc:
            return _erro(exc)
        if not messagebox.askyesno("Confirmar", f"Excluir a manutenção ID {mid}?"):
            return
        try:
            self.repo.excluir(mid)
        except Exception as exc:
            return _erro(exc)
        messagebox.showinfo("Sucesso", "Manutenção excluída.")
        self._limpar(); self.atualizar_tabela()

    def atualizar_tabela(self):
        self._carregar_veiculos()
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        try:
            for m in self.repo.listar():
                self.tabela.insert("", "end", values=(
                    m["id"], m["descricao"], m["data"],
                    f'{m["valor"]:.2f}', f'{m["placa"]} {m["marca"]} {m["modelo"]}'))
        except Exception as exc:
            _erro(exc)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg="#121212")

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background="#121212", foreground="#E0E0E0")

        style.configure("TFrame",
                        background="#121212")

        style.configure("TLabel",
                        background="#121212",
                        foreground="#E0E0E0")

        style.configure("TNotebook",
                        background="#121212",
                        borderwidth=0)

        style.configure("TNotebook.Tab",
                        background="#1C1C1C",
                        foreground="#B0B0B0",
                        padding=(15, 8))

        style.map("TNotebook.Tab",
                background=[("selected", "#3A3A3A")],
                foreground=[("selected", "#E0E0E0")])

        style.configure("Treeview",
                        background="#1C1C1C",
                        foreground="#E0E0E0",
                        fieldbackground="#1C1C1C",
                        bordercolor="#444444",
                        rowheight=30)

        style.configure("Treeview.Heading",
                        background="#252525",
                        foreground="#E0E0E0",
                        font=("Segoe UI", 10, "bold"))

        style.map("Treeview",
                background=[("selected", "#666666")])

        style.configure("TButton",
                        background="#3A3A3A",
                        foreground="#E0E0E0",
                        bordercolor="#444444",
                        padding=8)

        style.map("TButton",
                background=[("active", "#505050")])
        self.title("Controle de Veículos e Manutenções")
        self.geometry("900x520")        
        init_db()
        self.veiculos_repo = VeiculoRepository()
        self.manutencoes_repo = ManutencaoRepository()
        abas = ttk.Notebook(self)
        abas.pack(fill="both", expand=True)
        self.frame_manut = ManutencoesFrame(abas, self.manutencoes_repo, self.veiculos_repo)
        self.frame_veic = VeiculosFrame(
            abas, self.veiculos_repo, on_change=self.frame_manut.atualizar_tabela)
        abas.add(self.frame_veic, text="Veículos")
        abas.add(self.frame_manut, text="Manutenções")


if __name__ == "__main__":
    App().mainloop()
