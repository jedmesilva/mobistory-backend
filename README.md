# Mobistory Backend

Backend Python com FastAPI + PostgreSQL + IA para o aplicativo Mobistory.

## 🚀 Stack Tecnológica

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)
- **IA**: OpenAI + LangChain
- **Validação**: Pydantic V2
- **CORS**: Configurado para React Native

## 📁 Estrutura do Projeto

```
mobistory-backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py           # Autenticação (login, registro)
│   │   │   │   ├── users.py          # Gerenciamento de usuários
│   │   │   │   ├── vehicles.py       # CRUD de veículos
│   │   │   │   ├── conversations.py  # Conversas
│   │   │   │   ├── messages.py       # Mensagens
│   │   │   │   ├── contexts.py       # Contextos IA
│   │   │   │   ├── fueling.py        # Abastecimentos
│   │   │   │   └── maintenance.py    # Manutenções
│   │   │   └── api.py                # Router principal V1
│   │   └── deps.py                   # Dependências (get_db, get_current_user)
│   ├── core/
│   │   ├── config.py                 # Configurações (Settings)
│   │   ├── security.py               # JWT, hashing de senha
│   │   └── database.py               # Conexão com PostgreSQL
│   ├── models/
│   │   ├── base.py                   # Base model
│   │   ├── user.py                   # Model User
│   │   ├── vehicle.py                # Models Vehicle, Brand, Model
│   │   ├── conversation.py           # Model Conversation
│   │   ├── message.py                # Model Message
│   │   ├── context.py                # Model ConversationContext
│   │   ├── fueling.py                # Model Fueling
│   │   └── maintenance.py            # Model Maintenance
│   ├── schemas/
│   │   ├── user.py                   # Pydantic schemas para User
│   │   ├── vehicle.py                # Schemas para Vehicle
│   │   ├── conversation.py           # Schemas para Conversation
│   │   ├── message.py                # Schemas para Message
│   │   ├── context.py                # Schemas para Context
│   │   └── token.py                  # Schemas para JWT
│   ├── services/
│   │   ├── ai/
│   │   │   ├── agent.py              # IA Agent principal
│   │   │   ├── tools.py              # Tools para LangChain
│   │   │   ├── prompts.py            # Prompts templates
│   │   │   └── context_identifier.py # Identificador de contextos
│   │   └── storage.py                # Upload de arquivos
│   └── main.py                       # Entry point da aplicação
├── alembic/
│   ├── versions/                     # Migrations
│   ├── env.py                        # Config do Alembic
│   └── script.py.mako                # Template de migration
├── docker-compose.yml                # PostgreSQL + pgAdmin
├── Dockerfile                        # Build do backend
├── requirements.txt                  # Dependências Python
├── .env.example                      # Exemplo de variáveis de ambiente
├── .gitignore
└── README.md
```

## 🛠️ Setup Local (Desenvolvimento)

### Pré-requisitos

- Python 3.11 ou superior
- Docker e Docker Compose
- Git

### 1. Clonar o repositório

```bash
cd C:\Users\Dell\Desktop
# O projeto já deve estar em mobistory-backend/
```

### 2. Criar ambiente virtual Python

```bash
cd mobistory-backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Editar .env com seus valores
```

### 5. Subir banco de dados PostgreSQL

```bash
docker-compose up -d
```

Isso vai subir:
- PostgreSQL na porta 5432
- pgAdmin na porta 5050 (interface web)

### 6. Criar tabelas no banco (migrations)

```bash
# Gerar migration inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migrations
alembic upgrade head
```

### 7. Rodar o servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend rodando em**: http://localhost:8000
✅ **Documentação interativa**: http://localhost:8000/docs
✅ **pgAdmin**: http://localhost:5050

## 🐳 Deploy em Produção (VPS)

### Opção 1: Docker Compose (Recomendado)

```bash
# No servidor VPS
git clone seu-repositorio.git
cd mobistory-backend

# Configurar .env de produção
cp .env.example .env
nano .env  # editar valores

# Subir tudo com Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Opção 2: Sem Docker

```bash
# Instalar PostgreSQL no servidor
sudo apt install postgresql postgresql-contrib

# Criar banco
sudo -u postgres createdb mobistory_db

# Instalar Python e dependências
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Rodar migrations
alembic upgrade head

# Usar gunicorn para produção
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 Comandos Úteis

### Alembic (Migrations)

```bash
# Criar nova migration
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar todas as migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Ver histórico de migrations
alembic history
```

### Docker

```bash
# Ver logs
docker-compose logs -f

# Ver logs só do backend
docker-compose logs -f backend

# Parar tudo
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Reconstruir imagem
docker-compose build --no-cache
```

### PostgreSQL

```bash
# Acessar banco via Docker
docker-compose exec postgres psql -U mobistory -d mobistory_db

# Backup do banco
docker-compose exec postgres pg_dump -U mobistory mobistory_db > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U mobistory mobistory_db < backup.sql
```

## 🔑 Autenticação

O backend usa JWT (JSON Web Tokens) para autenticação.

### Fluxo:
1. **Registro**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login` → retorna `access_token`
3. **Usar token**: Incluir header `Authorization: Bearer {token}` em requests

### Exemplo (JavaScript/React Native):

```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'senha123' })
})
const { access_token } = await response.json()

// Usar token em requests
const vehicles = await fetch('http://localhost:8000/api/v1/vehicles', {
  headers: { 'Authorization': `Bearer ${access_token}` }
})
```

## 🤖 IA Agent

O sistema de IA usa LangChain + OpenAI para:
- Identificar contextos de mensagens
- Extrair dados estruturados (abastecimento, manutenção, etc)
- Interpretar linguagem natural brasileira

### Endpoint:
```
POST /api/v1/contexts/identify
{
  "message_id": "uuid-da-mensagem"
}
```

## 🌐 CORS

CORS configurado para aceitar requests de:
- `http://localhost:8081` (Expo dev)
- `exp://192.168.*.*:8081` (Expo LAN)
- Seus domínios de produção

## 📝 Licença

MIT
