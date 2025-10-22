# 🧪 Guia de Teste - Mobistory Backend API

## 🚀 Iniciar o backend

```bash
cd C:\Users\Dell\Desktop\mobistory-backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

✅ Backend rodando em: http://localhost:8000
✅ Documentação interativa: http://localhost:8000/docs

---

## 📋 Endpoints Disponíveis

### **Autenticação** (`/api/v1/auth`)
- ✅ `POST /api/v1/auth/register` - Registrar usuário
- ✅ `POST /api/v1/auth/login` - Login (retorna JWT token)
- ✅ `GET /api/v1/auth/me` - Dados do usuário atual

### **Veículos** (`/api/v1/vehicles`)
- ✅ `GET /api/v1/vehicles` - Listar veículos
- ✅ `POST /api/v1/vehicles` - Criar veículo
- ✅ `GET /api/v1/vehicles/{id}` - Obter veículo
- ✅ `PUT /api/v1/vehicles/{id}` - Atualizar veículo
- ✅ `DELETE /api/v1/vehicles/{id}` - Deletar veículo

### **Conversas** (`/api/v1/conversations`)
- ✅ `GET /api/v1/conversations` - Listar conversas
- ✅ `POST /api/v1/conversations` - Criar conversa
- ✅ `GET /api/v1/conversations/{id}` - Obter conversa
- ✅ `PUT /api/v1/conversations/{id}` - Atualizar conversa
- ✅ `DELETE /api/v1/conversations/{id}` - Deletar conversa

### **Mensagens** (`/api/v1/messages`)
- ✅ `GET /api/v1/messages?conversation_id={id}` - Listar mensagens
- ✅ `POST /api/v1/messages` - Enviar mensagem
- ✅ `GET /api/v1/messages/{id}` - Obter mensagem
- ✅ `PUT /api/v1/messages/{id}` - Atualizar mensagem

---

## 🎯 Fluxo de Teste Completo

### 1. Registrar novo usuário

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@mobistory.com",
    "password": "senha123",
    "full_name": "Usuario Teste"
  }'
```

**Resposta esperada:**
```json
{
  "id": "uuid-aqui",
  "email": "teste@mobistory.com",
  "full_name": "Usuario Teste",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-22T...",
  "updated_at": "2025-10-22T..."
}
```

### 2. Fazer login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@mobistory.com",
    "password": "senha123"
  }'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**⚠️ IMPORTANTE:** Copie o `access_token` para usar nos próximos requests!

### 3. Obter dados do usuário atual

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### 4. Criar marcas, modelos (preparar dados)

Antes de criar veículos, você precisa ter brands e models no banco.

**Opção A - Via SQL direto:**
```sql
-- Conectar ao PostgreSQL
docker-compose exec postgres psql -U mobistory -d mobistory_db

-- Inserir marcas
INSERT INTO brands (id, brand, created_at, updated_at)
VALUES
  (gen_random_uuid(), 'Fiat', NOW(), NOW()),
  (gen_random_uuid(), 'Volkswagen', NOW(), NOW()),
  (gen_random_uuid(), 'Chevrolet', NOW(), NOW());

-- Inserir modelos (pegar ID das marcas primeiro)
SELECT id, brand FROM brands;

INSERT INTO models (id, model, brand_id, created_at, updated_at)
VALUES
  (gen_random_uuid(), 'Uno', 'ID_DA_MARCA_FIAT', NOW(), NOW()),
  (gen_random_uuid(), 'Gol', 'ID_DA_MARCA_VW', NOW(), NOW());

-- Ver IDs criados
SELECT id, brand FROM brands;
SELECT id, model FROM models;
```

**Opção B - Criar endpoints de brands/models (recomendado para produção)**

### 5. Criar veículo

```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "ID_DA_MARCA_AQUI",
    "model_id": "ID_DO_MODELO_AQUI",
    "year": 2020,
    "nickname": "Meu Carro"
  }'
```

### 6. Listar veículos

```bash
curl http://localhost:8000/api/v1/vehicles \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### 7. Criar conversa

```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "ID_DO_VEICULO_AQUI",
    "title": "Conversa sobre manutenção"
  }'
```

### 8. Enviar mensagem

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "ID_DA_CONVERSA_AQUI",
    "content": "Abasteci 45 litros hoje",
    "message_type": "text",
    "sender_type": "user",
    "context_hint": "fueling"
  }'
```

### 9. Listar mensagens da conversa

```bash
curl "http://localhost:8000/api/v1/messages?conversation_id=ID_DA_CONVERSA_AQUI" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🌐 Testar na Documentação Interativa

A forma mais fácil é usar o Swagger UI:

1. Abrir http://localhost:8000/docs
2. Clicar em "POST /api/v1/auth/register" → Try it out → Executar
3. Clicar em "POST /api/v1/auth/login" → Try it out → Executar
4. **Copiar o token** retornado
5. Clicar no botão "Authorize" (cadeado verde no topo)
6. Colar o token no formato: `Bearer SEU_TOKEN_AQUI`
7. Agora todos os endpoints protegidos funcionarão!

---

## 🐛 Troubleshooting

### Erro: "Email already registered"
- Email já foi registrado. Use outro email ou faça login.

### Erro: "Invalid authentication credentials"
- Token expirou ou é inválido. Faça login novamente.

### Erro: "Vehicle not found"
- ID do veículo não existe ou não pertence ao usuário logado.

### Erro: "Brand/Model not found"
- Você precisa criar brands e models primeiro (ver passo 4).

---

## ✅ Checklist de Testes

- [ ] Registrar usuário
- [ ] Login
- [ ] Obter dados do usuário (me)
- [ ] Criar brand e model no banco
- [ ] Criar veículo
- [ ] Listar veículos
- [ ] Criar conversa
- [ ] Enviar mensagem
- [ ] Listar mensagens
- [ ] Atualizar veículo
- [ ] Deletar veículo

---

## 🎓 Próximos Passos

Depois de testar todos os endpoints, você pode:

1. **Implementar IA Agent** - Para identificar contextos automaticamente
2. **Criar endpoints de brands/models** - Para não precisar inserir via SQL
3. **Adicionar WebSockets** - Para chat em tempo real
4. **Integrar com React Native app** - Consumir a API no app mobile

Documentação completa em [NEXT_STEPS.md](NEXT_STEPS.md)
