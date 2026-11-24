# Sistema de Controle de Veículos e Histórico de Manutenções

Aplicação desenvolvida em dupla para cadastro e gerenciamento de veículos e suas manutenções, utilizando relacionamento **1:N** (um veículo pode ter várias manutenções vinculadas).

## Integrantes

- **Felipe de Souza Deoclecio**
- **Renan Siebra Braz**

---

## Visão Geral

O sistema é dividido em duas interfaces que compartilham o mesmo banco de dados SQLite (`prisma/dev.db`):

1. **Interface Desktop (Python + Tkinter):** tela para cadastro, consulta e gerenciamento de veículos e manutenções.
2. **API REST (Node.js + Express + Prisma):** rotas HTTP com middlewares de log e validação de dados/IDs.

## Tecnologias Utilizadas

- **Python 3** (Tkinter e `sqlite3`)
- **Node.js** (Express e Prisma ORM)
- **SQLite**

## Estrutura do Projeto

```text
CAR_API/
├── app.py                      # Interface gráfica em Tkinter
├── database.py                 # Conexão com SQLite e criação das tabelas
├── veiculo_repository.py       # Operações de banco para Veículos
├── manutencao_repository.py    # Operações de banco para Manutenções
├── collection-postman.json     # Coleção de requisições e testes de erro
├── prisma/
│   ├── schema.prisma           # Modelagem do banco (1:N)
│   └── migrations/             # Migrations do Prisma
└── src/
    ├── server.js               # Inicialização da API (porta 3000)
    ├── prisma.js               # Instância do Prisma Client
    ├── controllers/            # Regras de negócio (veículo e manutenção)
    ├── middlewares/            # Logger, validação de dados e validação de IDs
    └── routes/                 # Definição das rotas da API