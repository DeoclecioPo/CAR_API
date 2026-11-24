# Sistema de Controle de Veículos e Histórico de Manutenções

Aplicação para cadastro e gerenciamento de veículos e suas manutenções, explorando o relacionamento **1:N** (um **Veículo** possui várias **Manutenções**).

O projeto reúne duas frentes que compartilham a **mesma base SQLite** (`prisma/dev.db`):

1. **GUI Desktop em Python + Tkinter** — interface para o usuário final (entrega principal).
2. **API REST em Node.js + Express + Prisma** — backend original, preservado e completado.

## Tecnologias

- Python 3 + Tkinter (GUI) e `sqlite3` (padrão, sem dependências extras)
- Node.js + Express + Prisma
- SQLite em arquivo físico (`prisma/dev.db`)

## Estrutura

```
CAR_API/
├── app.py                      # GUI Tkinter (2 abas: Veículos e Manutenções)
├── database.py                 # Conexão SQLite compartilhada + criação das tabelas
├── veiculo_repository.py       # Regras de negócio/persistência de Veículos
├── manutencao_repository.py    # Regras de negócio/persistência de Manutenções
├── prisma/
│   ├── dev.db                  # Banco SQLite (compartilhado Python <-> Node)
│   ├── schema.prisma           # Modelagem Prisma (1:N)
│   └── migrations/             # Migration inicial
└── src/                        # API Node/Express preservada
    ├── server.js               #  http://localhost:3000
    ├── controllers/            # veiculo / manutencao
    └── routes/                 # veiculo / manutencao
```

## Banco de dados (relacionamento 1:N)

```sql
Veiculo    (id PK, placa UNIQUE, modelo, marca)
Manutencao (id PK, descricao, data TEXT 'AAAA-MM-DD', valor REAL,
            veiculoId FK -> Veiculo.id  ON DELETE RESTRICT)
```

Um veículo com manutenções vinculadas **não pode ser excluído** (regra `RESTRICT` + mensagem amigável na GUI/API).

## Como executar

### GUI Python/Tkinter (principal)

Requer Python 3.10+ com Tkinter (já incluído na maioria das instalações).

```bash
cd CAR_API
python app.py
```

> A GUI reusa `prisma/dev.db`. Se o arquivo não existir, as tabelas são criadas automaticamente. Para testes, use `CAR_DB_PATH=/caminho/outro.db python app.py`.

### API Node/Express (opcional)

```bash
cd CAR_API
cp .env.example .env   # ajuste o DATABASE_URL se necessário
npm install
npx prisma generate
npx prisma migrate dev   # apenas se o banco ainda não existir
npm start                # http://localhost:3000
```

## Endpoints da API

| Método | Rota | Função |
|---|---|---|
| POST | `/veiculos` | Cadastrar veículo |
| GET | `/veiculos` | Listar veículos (com manutenções) |
| GET | `/veiculos/:id` | Buscar veículo por ID |
| PUT | `/veiculos/:id` | Editar veículo |
| DELETE | `/veiculos/:id` | Excluir veículo (bloqueado se tiver manutenções) |
| POST | `/manutencoes` | Cadastrar manutenção |
| GET | `/manutencoes` | Listar manutenções (com veículo) |
| GET | `/manutencoes/:id` | Buscar manutenção por ID |
| PUT | `/manutencoes/:id` | Editar manutenção (inclusive `veiculoId`) |
| DELETE | `/manutencoes/:id` | Excluir manutenção |

## Validações

- Campos obrigatórios (placa, modelo, marca, descrição, data, valor, veículo).
- Placa no formato Mercosul/antigo (ex.: `ABC1D23`, `ABC1234`), única no banco.
- Data no formato `AAAA-MM-DD`; valor numérico e não negativo.
- IDs válidos: veículo/manutenção precisam existir; exclusão de veículo com manutenções é bloqueada.
- Exceções tratadas com mensagens amigáveis (caixas de diálogo na GUI e JSON `{ "erro": ... }` na API).
