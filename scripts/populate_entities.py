"""
Script para popular dados iniciais de entidades e vínculos
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.entity import Entity, VehicleEntityLink, EntityType, RelationshipType, LinkStatus

def populate_initial_data():
    """Popula dados iniciais de entidades e vínculos"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem entidades
        existing_entities = db.query(Entity).count()
        if existing_entities > 0:
            print(f"✅ Já existem {existing_entities} entidades no banco")
            return
        
        print("🔄 Populando dados iniciais...")
        
        # Criar entidades de teste
        entities = [
            Entity(
                id=uuid.uuid4(),
                entity_type=EntityType.PERSON,
                name="João Silva",
                email="joao.silva@email.com",
                phone="+55 11 98765-4321",
                document_number="123.456.789-00",
                active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Entity(
                id=uuid.uuid4(),
                entity_type=EntityType.PERSON,
                name="Maria Santos",
                email="maria.santos@email.com",
                phone="+55 11 97654-3210",
                document_number="987.654.321-00",
                active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Entity(
                id=uuid.uuid4(),
                entity_type=EntityType.PERSON,
                name="Pedro Costa",
                email="pedro.costa@email.com",
                phone="+55 11 96543-2109",
                document_number="456.789.123-00",
                active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            Entity(
                id=uuid.uuid4(),
                entity_type=EntityType.COMPANY,
                name="AutoLoc Veículos Ltda",
                email="contato@autoloc.com.br",
                phone="+55 11 3333-4444",
                document_number="12.345.678/0001-90",
                active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
        
        # Adicionar entidades ao banco
        for entity in entities:
            db.add(entity)
        
        db.commit()
        print(f"✅ Criadas {len(entities)} entidades")
        
        # Buscar um veículo existente para criar vínculos (usar consulta SQL direta)
        result = db.execute("SELECT id FROM vehicles LIMIT 1")
        vehicle_row = result.fetchone()
        
        if vehicle_row:
            vehicle_id = vehicle_row[0]
            print(f"🔗 Criando vínculos para o veículo {vehicle_id}")
            
            # Criar vínculos de teste
            links = [
                VehicleEntityLink(
                    id=uuid.uuid4(),
                    vehicle_id=vehicle_id,
                    entity_id=entities[0].id,  # João Silva como proprietário
                    relationship_type=RelationshipType.OWNER,
                    status=LinkStatus.ACTIVE,
                    start_date=datetime.utcnow() - timedelta(days=365),
                    active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
                VehicleEntityLink(
                    id=uuid.uuid4(),
                    vehicle_id=vehicle_id,
                    entity_id=entities[1].id,  # Maria Santos como condutora autorizada
                    relationship_type=RelationshipType.AUTHORIZED_DRIVER,
                    status=LinkStatus.ACTIVE,
                    start_date=datetime.utcnow() - timedelta(days=90),
                    active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
                VehicleEntityLink(
                    id=uuid.uuid4(),
                    vehicle_id=vehicle_id,
                    entity_id=entities[2].id,  # Pedro Costa como ex-locatário
                    relationship_type=RelationshipType.RENTER,
                    status=LinkStatus.TERMINATED,
                    start_date=datetime.utcnow() - timedelta(days=200),
                    end_date=datetime.utcnow() - timedelta(days=30),
                    notes="Contrato de locação encerrado",
                    active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
            ]
            
            # Adicionar vínculos ao banco
            for link in links:
                db.add(link)
            
            db.commit()
            print(f"✅ Criados {len(links)} vínculos")
        else:
            print("⚠️  Nenhum veículo encontrado para criar vínculos")
        
        print("🎉 Dados iniciais populados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao popular dados: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_initial_data()