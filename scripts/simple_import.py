"""
Script simplificado para importar dados básicos do Supabase para PostgreSQL
NOTA: Devido às diferenças de schema, apenas dados básicos serão importados
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


def import_brands():
    """Importa marcas"""
    print("\n--- Importando Brands ---")
    data = load_json("brands.json")

    for item in data:
        cur.execute("""
            INSERT INTO brands (id, brand, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                brand = EXCLUDED.brand,
                updated_at = EXCLUDED.updated_at
        """, (item["id"], item["brand"], item["created_at"], item["updated_at"]))

    conn.commit()
    print(f"[OK] {len(data)} brands importados")


def import_models():
    """Importa modelos"""
    print("\n--- Importando Models ---")
    data = load_json("models.json")

    for item in data:
        cur.execute("""
            INSERT INTO models (id, brand_id, model, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                brand_id = EXCLUDED.brand_id,
                model = EXCLUDED.model,
                updated_at = EXCLUDED.updated_at
        """, (item["id"], item["brand_id"], item["model"], item["created_at"], item["updated_at"]))

    conn.commit()
    print(f"[OK] {len(data)} models importados")


def import_model_versions():
    """Importa versões de modelos"""
    print("\n--- Importando Model Versions ---")
    data = load_json("model_versions.json")

    for item in data:
        cur.execute("""
            INSERT INTO model_versions (id, model_id, version, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                model_id = EXCLUDED.model_id,
                version = EXCLUDED.version,
                updated_at = EXCLUDED.updated_at
        """, (item["id"], item["model_id"], item["version"], item["created_at"], item["updated_at"]))

    conn.commit()
    print(f"[OK] {len(data)} model versions importados")


def import_colors():
    """Importa cores únicas"""
    print("\n--- Importando Colors ---")
    data = load_json("colors.json")

    # Extrair cores únicas
    unique_colors = {}
    for item in data:
        color_name = item["color"]
        if color_name not in unique_colors:
            unique_colors[color_name] = item

    for color_name, item in unique_colors.items():
        cur.execute("""
            INSERT INTO colors (id, color, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                color = EXCLUDED.color,
                updated_at = EXCLUDED.updated_at
        """, (item["id"], color_name, item["created_at"], item["updated_at"]))

    conn.commit()
    print(f"[OK] {len(unique_colors)} colors importados")


def main():
    """Função principal"""
    print("=" * 60)
    print("IMPORTACAO SIMPLIFICADA PARA POSTGRESQL")
    print("=" * 60)

    try:
        # Importar dados básicos compatíveis
        import_brands()
        import_models()
        import_model_versions()
        import_colors()

        print("\n" + "=" * 60)
        print("IMPORTACAO BASICA CONCLUIDA")
        print("=" * 60)
        print("\nNOTA: Veiculos, conversas e outros dados nao foram importados")
        print("devido a diferencas no schema. Sera necessario criar novos")
        print("registros atraves da API.")

    except Exception as e:
        print(f"\n[ERRO] {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
