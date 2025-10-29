"""
Script para atualizar dados do Corolla para teste
"""
from sqlalchemy import create_engine, text

# Conexão com o banco
engine = create_engine('postgresql://mobistory:mobistory_dev_password@localhost:5432/mobistory_db')

with engine.connect() as conn:
    # Pega o ID do Corolla
    result = conn.execute(text("""
        SELECT v.id, p.id as plate_id, c.id as color_id
        FROM vehicles v
        JOIN brands b ON v.brand_id = b.id
        JOIN models m ON v.model_id = m.id
        LEFT JOIN plates p ON v.vehicle_id = p.vehicle_id AND p.active = true
        LEFT JOIN colors c ON v.id = c.vehicle_id AND c.active = true
        WHERE m.model = 'Corolla'
        LIMIT 1
    """))

    row = result.fetchone()
    if row:
        vehicle_id, plate_id, color_id = row
        print(f"Vehicle ID: {vehicle_id}")
        print(f"Plate ID: {plate_id}")
        print(f"Color ID: {color_id}")

        # Atualiza o ano do veículo
        conn.execute(text("""
            UPDATE vehicles
            SET model_year = 2025, manufacture_year = 2025
            WHERE id = :vehicle_id
        """), {"vehicle_id": vehicle_id})

        # Atualiza a placa
        if plate_id:
            conn.execute(text("""
                UPDATE plates
                SET plate = 'XXX9Z99', state = 'SP'
                WHERE id = :plate_id
            """), {"plate_id": plate_id})

        # Atualiza a cor
        if color_id:
            conn.execute(text("""
                UPDATE colors
                SET color = 'Gold'
                WHERE id = :color_id
            """), {"color_id": color_id})

        conn.commit()
        print("\n✅ Corolla atualizado com sucesso!")
        print("  Ano: 2025")
        print("  Placa: XXX9Z99 (SP)")
        print("  Cor: Gold (Dourado)")
    else:
        print("❌ Corolla não encontrado!")
