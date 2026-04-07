# Sistema de Chamados — Secretaria de Piraí (SECTI)

Sistema web para registro e acompanhamento de chamados de operação da Prefeitura de Piraí, desenvolvido com Django.

---

## Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/)
- Git

---

## Configuração do Ambiente

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd Chamados_SECTI
```

### 2. Crie e ative o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> Após ativar, o terminal exibirá `(venv)` no início da linha.

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo e edite conforme necessário:

**Windows:**
```powershell
copy .env.example .env
```

**Linux / Mac:**
```bash
cp .env.example .env
```

Abra o `.env` e substitua o valor de `SECRET_KEY` por uma chave segura.

### 5. Aplique as migrações do banco de dados

```bash
python manage.py migrate
```

### 6. Crie um superusuário (acesso ao painel admin)

```bash
python manage.py createsuperuser
```

### 7. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Estrutura do Projeto

```
Chamados_SECTI/
│
├── apps/                   # Aplicativos do projeto
│   └── chamados/           # App principal
│       ├── migrations/     # Histórico de alterações no banco
│       ├── admin.py        # Configuração do painel administrativo
│       ├── apps.py         # Configuração do app
│       ├── models.py       # Modelo Chamado (banco de dados)
│       ├── urls.py         # Rotas do app
│       └── views.py        # Lógica das páginas
│
├── setup/                  # Configurações globais do projeto
│   ├── settings.py         # Configurações principais (banco, apps, templates...)
│   ├── urls.py             # Roteamento global
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/              # Arquivos HTML
│   ├── base.html           # Template base (todos os outros herdam dele)
│   └── chamados/
│       └── lista.html      # Página de listagem dos chamados
│
├── .env                    # Variáveis de ambiente (NÃO versionar)
├── .env.example            # Modelo do .env (pode versionar)
├── manage.py               # Utilitário de linha de comando do Django
├── requirements.txt        # Dependências do projeto
└── db.sqlite3              # Banco de dados local (NÃO versionar)
```

---

## Páginas Disponíveis

| URL | Descrição |
|---|---|
| `/chamados/` | Lista de chamados |
| `/admin/` | Painel administrativo do Django |

---

## Conceitos Django Utilizados

| Conceito | Onde encontrar |
|---|---|
| **Model** — representa uma tabela no banco | `apps/chamados/models.py` |
| **View** — lógica da página | `apps/chamados/views.py` |
| **Template** — HTML da página | `templates/chamados/` |
| **URL** — mapeamento de rotas | `apps/chamados/urls.py` e `setup/urls.py` |
| **Admin** — interface automática de CRUD | `apps/chamados/admin.py` |

---

## Próximos Passos Sugeridos

- [ ] Criar formulário para abrir novos chamados
- [ ] Adicionar página de detalhes de um chamado
- [ ] Implementar login/logout para identificar o solicitante
- [ ] Associar cada chamado a um usuário (FK para `User`)
- [ ] Adicionar campo de prioridade e categoria ao modelo
