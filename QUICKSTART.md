# 🚀 Guia Rápido - Mobistory Backend

## Primeiros Passos

### 1️⃣ Criar ambiente virtual e instalar dependências

```bash
cd C:\Users\Dell\Desktop\mobistory-backend

# Criar venv
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Configurar .env

```bash
# Copiar exemplo
copy .env.example .env

# Editar .env e adicionar sua OpenAI API Key
# OPENAI_API_KEY=sk-xxx
```

### 3️⃣ Subir PostgreSQL

```bash
docker-compose up -d
```

Aguardar ~10 segundos para o PostgreSQL iniciar completamente.

### 4️⃣ Criar migrations e aplicar

```bash
# Gerar migration inicial com todos os models
alembic revision --autogenerate -m "Initial migration"

# Aplicar no banco
alembic upgrade head
```

### 5️⃣ Rodar servidor

```bash
uvicorn app.main:app --reload
```

✅ **Backend rodando!**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (user: admin@mobistory.local, pass: admin)

---

## 📊 Acessar pgAdmin

1. Abrir http://localhost:5050
2. Login: `admin@mobistory.local` / `admin`
3. Add Server:
   - Name: `Mobistory`
   - Host: `postgres` (se dentro do Docker) ou `localhost`
   - Port: `5432`
   - Username: `mobistory`
   - Password: `mobistory_dev_password`

---

## 🔧 Comandos Úteis

```bash
# Ver logs do PostgreSQL
docker-compose logs -f postgres

# Parar PostgreSQL
docker-compose down

# Resetar banco (CUIDADO: apaga tudo)
docker-compose down -v

# Criar nova migration depois de mudar models
alembic revision --autogenerate -m "descrição"
alembic upgrade head

# Reverter última migration
alembic downgrade -1
```

---

## 📝 Próximos Passos

Agora que o backend está rodando, você pode:

1. **Criar endpoints de autenticação** (`app/api/v1/endpoints/auth.py`)
2. **Criar endpoints de veículos** (`app/api/v1/endpoints/vehicles.py`)
3. **Implementar IA Agent** (`app/services/ai/agent.py`)
4. **Integrar com o app React Native**

Veja a documentação completa no [README.md](README.md)
