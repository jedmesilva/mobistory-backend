# 🚀 Comandos Rápidos - Mobistory Backend

## Setup Inicial (Primeira Vez)

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Copiar .env
copy .env.example .env  # Windows
cp .env.example .env  # Linux/Mac

# 5. Iniciar PostgreSQL
docker-compose up -d

# 6. Criar tabelas
alembic upgrade head
```

---

## Desenvolvimento Diário

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**URLs:**
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- pgAdmin: http://localhost:5050

---

## Docker

```bash
# Iniciar containers (PostgreSQL + pgAdmin)
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down

# Parar e limpar tudo (CUIDADO: apaga dados)
docker-compose down -v
```

---

## Banco de Dados

```bash
# Criar nova migration
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Ver histórico
alembic history

# Ver migration atual
alembic current
```

---

## Testes Rápidos

### Registrar e Logar
```bash
# Registrar
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "senha123", "full_name": "Test User"}'

# Login (copiar o access_token da resposta)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "senha123"}'

# Definir token
export TOKEN="cole_seu_token_aqui"  # Linux/Mac
set TOKEN=cole_seu_token_aqui  # Windows CMD
$env:TOKEN="cole_seu_token_aqui"  # Windows PowerShell

# Testar autenticação
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Criar Dados Base
```bash
# Criar marca
curl -X POST http://localhost:8000/api/v1/catalog/brands \
  -H "Content-Type: application/json" \
  -d '{"brand": "Fiat"}'

# Criar modelo (usar brand_id da resposta anterior)
curl -X POST http://localhost:8000/api/v1/catalog/models \
  -H "Content-Type: application/json" \
  -d '{"model": "Uno", "brand_id": "UUID_DA_MARCA"}'

# Criar versão (usar model_id da resposta anterior)
curl -X POST http://localhost:8000/api/v1/catalog/versions \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0 Vivace", "model_id": "UUID_DO_MODELO"}'
```

### Criar Veículo
```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "UUID_DA_MARCA",
    "model_id": "UUID_DO_MODELO",
    "version_id": "UUID_DA_VERSAO",
    "year": 2020,
    "nickname": "Meu Uno"
  }'
```

---

## Python

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar nova dependência
pip install nome-do-pacote
pip freeze > requirements.txt  # Atualizar requirements.txt

# Limpar cache
pip cache purge
```

---

## Git

```bash
# Status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "Descrição das mudanças"

# Push
git push origin main
```

---

## Produção

```bash
# Rodar com Gunicorn (produção)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Rodar em background
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --daemon

# Ver processos
ps aux | grep gunicorn

# Matar processo
pkill gunicorn
```

---

## Troubleshooting

### Porta já em uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Recriar banco de dados
```bash
# Parar containers
docker-compose down -v

# Iniciar novamente
docker-compose up -d

# Recriar tabelas
alembic upgrade head
```

### Limpar migrations
```bash
# Deletar migrations antigas
rm alembic/versions/*.py

# Criar nova migration inicial
alembic revision --autogenerate -m "initial"

# Aplicar
alembic upgrade head
```

---

## Atalhos Úteis

### Testar tudo rapidamente via Swagger
1. Abra http://localhost:8000/docs
2. Clique em "Authorize" (cadeado no topo direito)
3. Faça login em `/auth/login`
4. Cole o token no campo "Value" (formato: `Bearer SEU_TOKEN`)
5. Clique em "Authorize"
6. Agora todos os endpoints protegidos funcionarão!

### Acessar PostgreSQL via pgAdmin
1. Abra http://localhost:5050
2. Login: `admin@mobistory.local` / `admin`
3. Add Server:
   - Name: `Mobistory`
   - Host: `postgres` (dentro do Docker) ou `localhost`
   - Port: `5432`
   - User: `mobistory`
   - Password: `mobistory_dev_password`

### Acessar PostgreSQL via CLI
```bash
# Via Docker
docker exec -it mobistory-postgres psql -U mobistory -d mobistory_db

# Comandos úteis do psql
\dt          # Listar tabelas
\d users     # Ver estrutura da tabela users
\q           # Sair
```

---

## Variáveis de Ambiente (.env)

```env
# Banco de Dados
DATABASE_URL=postgresql://mobistory:mobistory_dev_password@localhost:5432/mobistory_db

# JWT
SECRET_KEY=sua_chave_secreta_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 dias

# OpenAI (para IA futura)
OPENAI_API_KEY=sua_chave_openai_aqui

# CORS
CORS_ORIGINS=["http://localhost:8081","http://localhost:19006"]

# Storage
STORAGE_TYPE=local
STORAGE_PATH=./uploads
```

---

## 📞 Ajuda

- **Documentação**: Ver `README.md`, `TESTING.md`, `API_COMPLETE.md`
- **Status**: Ver `STATUS.md`
- **Próximos passos**: Ver `NEXT_STEPS.md`
- **Issues conhecidas**: Ver Issues no repositório

---

**Última atualização**: 2025-10-22
