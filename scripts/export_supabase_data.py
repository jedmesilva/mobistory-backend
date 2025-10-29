"""
Script para exportar dados do Supabase para arquivos JSON
"""
import os
import json
from supabase import create_client, Client
from datetime import datetime

# Configurações do Supabase
SUPABASE_URL = "https://fsjncmqncdjevxvikdxo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZzam5jbXFuY2RqZXZ4dmlrZHhvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDUxMzIxOSwiZXhwIjoyMDc2MDg5MjE5fQ.3dFmz_fF1L8nEtgw4x5Wm6BD6TZvSUImi6LL_DTiHFA"

# Criar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Diretório para salvar os exports
EXPORT_DIR = "supabase_exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_table(table_name: str):
    """Exporta uma tabela do Supabase para JSON"""
    print(f"\nExportando tabela: {table_name}")

    try:
        # Buscar todos os registros da tabela
        response = supabase.table(table_name).select("*").execute()
        data = response.data

        # Salvar em arquivo JSON
        filename = f"{EXPORT_DIR}/{table_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        print(f"[OK] {table_name}: {len(data)} registros exportados")
        return len(data)

    except Exception as e:
        print(f"[SKIP] {table_name}: {str(e)[:100]}")
        return 0


def main():
    """Função principal"""
    print("=" * 60)
    print("EXPORTACAO DE DADOS DO SUPABASE")
    print("=" * 60)

    # Lista de tabelas para exportar (na ordem correta devido às FKs)
    tables = [
        # Tabelas base (sem FK)
        "countries",
        "brands",
        "fuels",
        "vehicle_categories",

        # Tabelas com FK de primeiro nível
        "models",
        "plate_types",

        # Tabelas com FK de segundo nível
        "model_versions",

        # Veículos (depende de várias tabelas)
        "vehicles",

        # Dados relacionados a veículos
        "vehicle_registrations",
        "plates",
        "colors",
        "vehicle_fuels",

        # Entidades e links (se existirem)
        "entities",
        "entity_vehicles",

        # Conversas
        "conversations",
        "conversation_contexts",
        "messages",

        # Registros de manutenção e abastecimento
        "vehicle_odometer",
        "vehicle_tank",
        "fueling",
        "maintenance",

        # Momentos (se existir)
        "moments",
    ]

    total_records = 0
    successful_tables = 0

    for table in tables:
        count = export_table(table)
        if count > 0:
            successful_tables += 1
            total_records += count

    print("\n" + "=" * 60)
    print(f"EXPORTACAO CONCLUIDA")
    print(f"Tabelas exportadas: {successful_tables}")
    print(f"Total de registros: {total_records}")
    print(f"Arquivos salvos em: {EXPORT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
