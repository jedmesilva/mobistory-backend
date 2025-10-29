"""
Script simplificado para popular dados iniciais usando SQL direto
"""
import uuid
from datetime import datetime, timedelta
import psycopg2
from app.core.config import settings

def populate_with_sql():
    """Popula dados usando SQL direto"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(settings.DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔄 Conectado ao banco, verificando dados...")
        
        # Verificar se já existem entidades
        cursor.execute("SELECT COUNT(*) FROM entities")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Já existem {count} entidades no banco")
            return
        
        print("🔄 Populando entidades...")
        
        # Criar entidades
        entities = [
            {
                'id': str(uuid.uuid4()),
                'name': 'João Silva',
                'email': 'joao.silva@email.com',
                'phone': '+55 11 98765-4321',
                'document': '123.456.789-00',
                'type': 'PERSON'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Maria Santos',
                'email': 'maria.santos@email.com',
                'phone': '+55 11 97654-3210',
                'document': '987.654.321-00',
                'type': 'PERSON'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Pedro Costa',
                'email': 'pedro.costa@email.com',
                'phone': '+55 11 96543-2109',
                'document': '456.789.123-00',
                'type': 'PERSON'
            }
        ]
        
        # Inserir entidades
        for entity in entities:
            cursor.execute("""
                INSERT INTO entities (id, entity_type, name, email, phone, document_number, active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                entity['id'],
                entity['type'],
                entity['name'],
                entity['email'],
                entity['phone'],
                entity['document'],
                True,
                datetime.utcnow(),
                datetime.utcnow()
            ))
        
        print(f"✅ Criadas {len(entities)} entidades")
        
        # Buscar um veículo para criar vínculos
        cursor.execute("SELECT id FROM vehicles LIMIT 1")
        vehicle = cursor.fetchone()
        
        if vehicle:
            vehicle_id = vehicle[0]
            print(f"🔗 Criando vínculos para veículo {vehicle_id}")
            
            # Criar vínculos
            links = [
                {
                    'id': str(uuid.uuid4()),
                    'vehicle_id': str(vehicle_id),
                    'entity_id': entities[0]['id'],
                    'relationship_type': 'OWNER',
                    'status': 'ACTIVE',
                    'start_date': datetime.utcnow() - timedelta(days=365)
                },
                {
                    'id': str(uuid.uuid4()),
                    'vehicle_id': str(vehicle_id),
                    'entity_id': entities[1]['id'],
                    'relationship_type': 'AUTHORIZED_DRIVER',
                    'status': 'ACTIVE',
                    'start_date': datetime.utcnow() - timedelta(days=90)
                },
                {
                    'id': str(uuid.uuid4()),
                    'vehicle_id': str(vehicle_id),
                    'entity_id': entities[2]['id'],
                    'relationship_type': 'RENTER',
                    'status': 'TERMINATED',
                    'start_date': datetime.utcnow() - timedelta(days=200),
                    'end_date': datetime.utcnow() - timedelta(days=30)
                }
            ]
            
            # Inserir vínculos
            for link in links:
                cursor.execute("""
                    INSERT INTO vehicle_entity_links 
                    (id, vehicle_id, entity_id, relationship_type, status, start_date, end_date, active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    link['id'],
                    link['vehicle_id'],
                    link['entity_id'],
                    link['relationship_type'],
                    link['status'],
                    link['start_date'],
                    link.get('end_date'),
                    True,
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
            
            print(f"✅ Criados {len(links)} vínculos")
        
        # Commit das mudanças
        conn.commit()
        print("🎉 Dados populados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    populate_with_sql()