"""
Script para criar um usuário de teste no PostgreSQL
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import uuid

def create_test_user():
    """Cria um usuário de teste"""
    db = SessionLocal()

    try:
        # Verificar se já existe um usuário com este email
        existing_user = db.query(User).filter(User.email == "test@mobistory.com").first()

        if existing_user:
            print(f"Usuario ja existe: {existing_user.email} (ID: {existing_user.id})")
            return existing_user.id

        # Criar novo usuário
        user = User(
            id=uuid.uuid4(),
            email="test@mobistory.com",
            hashed_password=get_password_hash("test123"),
            full_name="Usuario de Teste",
            is_active=True,
            is_superuser=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Usuario criado com sucesso!")
        print(f"Email: {user.email}")
        print(f"Senha: test123")
        print(f"ID: {user.id}")

        return user.id

    except Exception as e:
        print(f"Erro ao criar usuario: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    user_id = create_test_user()
    print(f"\nUser ID para usar na importacao: {user_id}")
