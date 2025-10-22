# 📋 Próximos Passos - Mobistory Backend

## ✅ O que já está pronto:

- [x] Estrutura completa do projeto
- [x] Models do banco (User, Vehicle, Conversation, Message, Context, Fueling, Maintenance)
- [x] Core modules (config, database, security/JWT)
- [x] Schemas Pydantic para validação
- [x] API dependencies (get_current_user)
- [x] Docker Compose com PostgreSQL
- [x] Alembic configurado para migrations
- [x] FastAPI app principal

## 🚧 O que falta implementar:

### 1. **Endpoints de Autenticação** (PRIORITÁRIO)
Criar `app/api/v1/endpoints/auth.py`:
- `POST /api/v1/auth/register` - Registrar novo usuário
- `POST /api/v1/auth/login` - Login e retornar JWT token
- `GET /api/v1/auth/me` - Obter dados do usuário atual

### 2. **Endpoints de Veículos**
Criar `app/api/v1/endpoints/vehicles.py`:
- `GET /api/v1/vehicles` - Listar veículos do usuário
- `POST /api/v1/vehicles` - Criar veículo
- `GET /api/v1/vehicles/{id}` - Obter veículo específico
- `PUT /api/v1/vehicles/{id}` - Atualizar veículo
- `DELETE /api/v1/vehicles/{id}` - Deletar veículo

### 3. **Endpoints de Conversas**
Criar `app/api/v1/endpoints/conversations.py`:
- `GET /api/v1/conversations` - Listar conversas
- `POST /api/v1/conversations` - Criar conversa
- `GET /api/v1/conversations/{id}` - Obter conversa com mensagens

### 4. **Endpoints de Mensagens**
Criar `app/api/v1/endpoints/messages.py`:
- `GET /api/v1/messages` - Listar mensagens de uma conversa
- `POST /api/v1/messages` - Enviar mensagem
- `PUT /api/v1/messages/{id}` - Atualizar mensagem

### 5. **IA Agent com LangChain** (IMPORTANTE)
Criar `app/services/ai/`:
- `agent.py` - Agent principal com LangChain
- `tools.py` - Tools para buscar dados (fueling, maintenance, etc)
- `prompts.py` - Templates de prompts
- `context_identifier.py` - Lógica de identificação de contextos

Endpoint:
- `POST /api/v1/contexts/identify` - Identificar contexto de mensagem

### 6. **Integrar Routers**
Criar `app/api/v1/api.py` e integrar todos os routers no `main.py`

---

## 📝 Template para Endpoints

### Exemplo: `app/api/v1/endpoints/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models import User
from app.schemas import UserCreate, UserLogin, Token, User as UserSchema
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Criar usuário
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Login e retornar token JWT"""
    user = db.query(User).filter(User.email == user_in.email).first()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Obter dados do usuário atual"""
    return current_user
```

### Integrar router em `app/api/v1/api.py`:

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, vehicles, conversations, messages

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
```

### Integrar em `app/main.py`:

```python
from app.api.v1.api import api_router

app.include_router(api_router, prefix="/api/v1")
```

---

## 🤖 Template para IA Agent

### `app/services/ai/agent.py`

```python
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from .tools import search_fueling, search_maintenance, search_contexts
from .prompts import SYSTEM_PROMPT

def create_context_agent():
    """Criar agent para identificar contextos"""

    # LLM
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o",
        temperature=0.3,
    )

    # Tools
    tools = [
        Tool(
            name="search_fueling",
            func=search_fueling,
            description="Busca registros de abastecimento do veículo",
        ),
        Tool(
            name="search_maintenance",
            func=search_maintenance,
            description="Busca registros de manutenção do veículo",
        ),
        Tool(
            name="search_contexts",
            func=search_contexts,
            description="Busca contextos anteriores da conversa",
        ),
    ]

    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor


async def identify_context(message_id: str, db):
    """Identificar contexto de uma mensagem"""
    agent = create_context_agent()

    # Buscar mensagem
    message = db.query(Message).filter(Message.id == message_id).first()

    # Executar agent
    result = agent.invoke({
        "input": f"Mensagem: {message.content}\\nContext hint: {message.context_hint}",
    })

    return result
```

---

## ⚡ Como testar

1. **Iniciar backend**:
```bash
cd C:\\Users\\Dell\\Desktop\\mobistory-backend
venv\\Scripts\\activate
uvicorn app.main:app --reload
```

2. **Testar endpoints na documentação**:
- Abrir http://localhost:8000/docs
- Testar cada endpoint interativamente

3. **Criar primeiro usuário**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "password": "senha123", "full_name": "User Test"}'
```

4. **Fazer login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "password": "senha123"}'
```

5. **Usar token**:
```bash
curl http://localhost:8000/api/v1/vehicles \\
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🎯 Ordem Recomendada de Implementação:

1. ✅ **Auth endpoints** - Para poder autenticar
2. ✅ **Vehicles endpoints** - CRUD básico
3. ✅ **Conversations endpoints**
4. ✅ **Messages endpoints**
5. ✅ **IA Agent** - Identificação de contextos
6. ✅ **Testar integração com app React Native**

---

**Quer que eu continue implementando os endpoints ou prefere fazer sozinho?** 😊
