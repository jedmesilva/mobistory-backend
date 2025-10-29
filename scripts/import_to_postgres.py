"""
Script para importar dados do Supabase para o PostgreSQL local
"""
import os
import json
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path para importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models import brand, model, color
from app.core.database import Base, SessionLocal

# Diretório com os arquivos JSON exportados
EXPORT_DIR = "supabase_exports"


def load_json(filename: str):
    """Carrega dados de um arquivo JSON"""
    filepath = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[SKIP] {filename} nao encontrado")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[LOAD] {filename}: {len(data)} registros")
    return data


def import_brands(db):
    """Importa marcas de veículos"""
    print("\n--- Importando Brands ---")
    data = load_json("brands.json")

    for item in data:
        # Inserir diretamente usando SQL raw para preservar IDs e timestamps
        query = text("""
            INSERT INTO brands (id, brand, created_at, updated_at)
            VALUES (:id, :brand, :created_at, :updated_at)
            ON CONFLICT (id) DO NOTHING
        """)

        db.execute(query, {
            "id": item["id"],
            "brand": item["brand"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        })

    db.commit()
    print(f"[OK] Brands importados: {len(data)}")


def import_models(db):
    """Importa modelos de veículos"""
    print("\n--- Importando Models ---")
    data = load_json("models.json")

    for item in data:
        query = text("""
            INSERT INTO models (id, brand_id, model, created_at, updated_at)
            VALUES (:id, :brand_id, :model, :created_at, :updated_at)
            ON CONFLICT (id) DO NOTHING
        """)

        db.execute(query, {
            "id": item["id"],
            "brand_id": item["brand_id"],
            "model": item["model"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        })

    db.commit()
    print(f"[OK] Models importados: {len(data)}")


def import_model_versions(db):
    """Importa versões de modelos"""
    print("\n--- Importando Model Versions ---")
    data = load_json("model_versions.json")

    for item in data:
        query = text("""
            INSERT INTO model_versions (id, model_id, version, created_at, updated_at)
            VALUES (:id, :model_id, :version, :created_at, :updated_at)
            ON CONFLICT (id) DO NOTHING
        """)

        db.execute(query, {
            "id": item["id"],
            "model_id": item["model_id"],
            "version": item["version"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        })

    db.commit()
    print(f"[OK] Model Versions importados: {len(data)}")


def import_colors(db):
    """Importa cores de veículos"""
    print("\n--- Importando Colors ---")
    data = load_json("colors.json")

    # No Supabase, colors tem vehicle_id (é específico de cada veículo)
    # No novo schema, colors é uma tabela de referência separada
    # Vamos extrair cores únicas
    unique_colors = {}
    for item in data:
        color_name = item["color"]
        if color_name not in unique_colors:
            unique_colors[color_name] = item

    for color_name, item in unique_colors.items():
        query = text("""
            INSERT INTO colors (id, color, created_at, updated_at)
            VALUES (:id, :color, :created_at, :updated_at)
            ON CONFLICT (id) DO NOTHING
        """)

        db.execute(query, {
            "id": item["id"],
            "color": color_name,
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        })

    db.commit()
    print(f"[OK] Colors importados: {len(unique_colors)}")


def import_vehicles(db):
    """Importa veículos"""
    print("\n--- Importando Vehicles ---")
    vehicles_data = load_json("vehicles.json")
    colors_data = load_json("colors.json")
    plates_data = load_json("plates.json")

    # Criar mapa de vehicle_id -> color_id
    vehicle_colors = {}
    for color in colors_data:
        if color.get("active", True):
            vehicle_colors[color["vehicle_id"]] = color["id"]

    for item in vehicles_data:
        # Buscar a cor ativa deste veículo
        color_id = vehicle_colors.get(item["id"])

        # No Supabase: chassis, model_year, manufacture_year, brand_id, model_id, version_id, category_id
        # No novo schema: user_id (novo), brand_id, model_id, version_id, color_id (novo), year (model_year), nickname (null)

        # Como não temos user_id nos dados do Supabase, vamos criar um usuário padrão
        # ou pular a importação de veículos por enquanto

        # Por enquanto, vamos pular a importação direta de veículos
        # pois precisamos de user_id que não existe no Supabase
        pass

    print(f"[SKIP] Vehicles precisam de user_id - sera necessario ajuste manual")


def import_conversations(db):
    """Importa conversas"""
    print("\n--- Importando Conversations ---")
    data = load_json("conversations.json")

    # Conversations no Supabase podem ter estrutura diferente
    # Vamos verificar a estrutura primeiro
    if data:
        print(f"[INFO] Exemplo de conversation: {list(data[0].keys())}")

    # Por enquanto, pular importação de conversations
    # pois precisam de user_id e vehicle_id válidos
    print(f"[SKIP] Conversations precisam de user_id e vehicle_id - ajuste manual necessario")


def main():
    """Função principal"""
    print("=" * 60)
    print("IMPORTACAO DE DADOS PARA POSTGRESQL")
    print("=" * 60)

    # Criar sessão do banco
    db = SessionLocal()

    try:
        # Importar tabelas base (sem FK complexas)
        import_brands(db)
        import_models(db)
        import_model_versions(db)
        import_colors(db)

        # Importar dados que dependem de user_id
        # (precisam de tratamento especial)
        import_vehicles(db)
        import_conversations(db)

        print("\n" + "=" * 60)
        print("IMPORTACAO CONCLUIDA")
        print("=" * 60)
        print("\nNOTA: Veiculos e conversas precisam de user_id.")
        print("Crie um usuario primeiro, depois ajuste a importacao.")

    except Exception as e:
        print(f"\n[ERRO] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
