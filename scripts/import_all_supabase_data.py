"""
Script para importar TODOS os dados do Supabase para PostgreSQL
COM O SCHEMA CORRETO (igual ao Supabase)
"""
import os
import json
import psycopg2
from datetime import datetime

# Conexão com PostgreSQL
conn = psycopg2.connect('postgresql://mobistory:mobistory_dev_password@localhost:5432/mobistory_db')
cur = conn.cursor()

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


def import_table(table_name, data, columns):
    """Importa dados genéricos para uma tabela"""
    if not data:
        print(f"[SKIP] {table_name}: sem dados")
        return 0

    print(f"\n--- Importando {table_name} ---")

    count = 0
    for item in data:
        # Pegar apenas as colunas que existem no item
        available_cols = [col for col in columns if col in item]
        values = [item[col] for col in available_cols]
        placeholders = ','.join(['%s'] * len(available_cols))

        query = f"""
            INSERT INTO {table_name} ({','.join(available_cols)})
            VALUES ({placeholders})
            ON CONFLICT (id) DO UPDATE SET
                updated_at = EXCLUDED.updated_at
        """

        try:
            cur.execute(query, values)
            count += 1
        except Exception as e:
            print(f"[ERRO] {table_name} - {e}")
            print(f"Item: {item}")

    conn.commit()
    print(f"[OK] {table_name}: {count} registros importados")
    return count


def main():
    """Função principal"""
    print("=" * 60)
    print("IMPORTACAO COMPLETA DE DADOS DO SUPABASE")
    print("=" * 60)

    total_records = 0

    # Importar na ordem correta (respeitando FKs)

    # 1. Tabelas base (sem FK)
    data = load_json("countries.json")
    total_records += import_table("countries", data, ["id", "name", "iso_code", "iso3_code", "active", "created_at", "updated_at"])

    data = load_json("brands.json")
    total_records += import_table("brands", data, ["id", "brand", "verified", "active", "created_at", "updated_at"])

    data = load_json("fuels.json")
    total_records += import_table("fuels", data, ["id", "name", "type", "description", "active", "created_at", "updated_at"])

    data = load_json("vehicle_categories.json")
    total_records += import_table("vehicle_categories", data, ["id", "category", "description", "active", "created_at", "updated_at"])

    # 2. Tabelas com FK de primeiro nível
    data = load_json("models.json")
    total_records += import_table("models", data, ["id", "brand_id", "model", "verified", "active", "created_at", "updated_at"])

    data = load_json("plate_types.json")
    total_records += import_table("plate_types", data, ["id", "country_id", "name", "description", "format_pattern", "valid_from", "valid_until", "active", "created_at", "updated_at"])

    # 3. Tabelas com FK de segundo nível
    data = load_json("model_versions.json")
    total_records += import_table("model_versions", data, ["id", "model_id", "version", "active", "created_at", "updated_at"])

    # 4. Veículos
    data = load_json("vehicles.json")
    total_records += import_table("vehicles", data, ["id", "brand_id", "model_id", "version_id", "category_id", "chassis", "model_year", "manufacture_year", "active", "created_at", "updated_at"])

    # 5. Dados relacionados a veículos
    data = load_json("vehicle_registrations.json")
    total_records += import_table("vehicle_registrations", data, ["id", "vehicle_id", "country_id", "registration_number", "registration_type", "start_date", "end_date", "active", "created_at", "updated_at"])

    data = load_json("plates.json")
    total_records += import_table("plates", data, ["id", "vehicle_id", "plate_type_id", "plate", "state", "licensing_country_id", "start_date", "end_date", "active", "created_at", "updated_at"])

    data = load_json("colors.json")
    total_records += import_table("colors", data, ["id", "vehicle_id", "color", "start_date", "end_date", "active", "created_at", "updated_at"])

    data = load_json("vehicle_fuels.json")
    total_records += import_table("vehicle_fuels", data, ["id", "vehicle_id", "fuel_id", "start_date", "end_date", "active", "notes", "created_at", "updated_at"])

    # 6. Entidades
    data = load_json("entities.json")
    total_records += import_table("entities", data, ["id", "entity_type", "name", "email", "phone", "document_number", "ai_model", "ai_capabilities", "device_serial", "device_type", "legal_id", "organization_type", "metadata", "active", "created_at", "updated_at"])

    # 7. Conversas
    data = load_json("conversations.json")
    total_records += import_table("conversations", data, ["id", "vehicle_id", "entity_id", "title", "status", "last_message_at", "last_message_preview", "unread_count", "metadata", "active", "created_at", "updated_at"])

    data = load_json("messages.json")
    total_records += import_table("messages", data, ["id", "conversation_id", "sender_id", "message_type", "content", "media_urls", "metadata", "status", "sent_at", "delivered_at", "read_at", "reply_to_message_id", "reactions", "edited", "edited_at", "deleted", "deleted_at", "created_at"])

    data = load_json("conversation_contexts.json")
    # Esta tabela não existe no novo schema - skip

    # 8. Momentos
    data = load_json("moments.json")
    total_records += import_table("moments", data, ["id", "vehicle_id", "entity_id", "caption", "type", "location", "tags", "active", "created_at", "updated_at"])

    print("\n" + "=" * 60)
    print("IMPORTACAO CONCLUIDA")
    print(f"Total de registros: {total_records}")
    print("=" * 60)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
