"""
Script para popular tipos de placas brasileiras
Incluindo sistema antigo e Mercosul
"""
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.vehicle import PlateType
import uuid

# Criar engine e session
engine = create_engine(settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
SessionLocal = sessionmaker(bind=engine)

# Dados dos tipos de placas brasileiras
PLATE_TYPES_BR = [
    # ===== SISTEMA MERCOSUL (Atual - 2018+) =====
    {
        "code": "BR_MERCOSUL_PARTICULAR",
        "name": "Mercosul - Particular",
        "description": "Placa padrão Mercosul para veículos particulares no Brasil (2018+)",
        "country": "BR",
        "category": "particular",
        "format_pattern": "AAA9A99",
        "format_example": "ABC1D23",
        "plate_color_name": "Branca com faixa azul",
        "background_color_hex": "#FFFFFF",
        "text_color_hex": "#000000",
    },
    {
        "code": "BR_MERCOSUL_COMERCIAL",
        "name": "Mercosul - Comercial/Aluguel",
        "description": "Placa padrão Mercosul para veículos comerciais e de aluguel no Brasil",
        "country": "BR",
        "category": "comercial",
        "format_pattern": "AAA9A99",
        "format_example": "ABC1D23",
        "plate_color_name": "Branca com faixa preta",
        "background_color_hex": "#FFFFFF",
        "text_color_hex": "#000000",
    },
    {
        "code": "BR_MERCOSUL_COLECAO",
        "name": "Mercosul - Coleção/Histórico",
        "description": "Placa padrão Mercosul para veículos de coleção e históricos",
        "country": "BR",
        "category": "colecao",
        "format_pattern": "AAA9A99",
        "format_example": "ABC1D23",
        "plate_color_name": "Branca com faixa dourada",
        "background_color_hex": "#FFFFFF",
        "text_color_hex": "#000000",
    },
    {
        "code": "BR_MERCOSUL_APRENDIZAGEM",
        "name": "Mercosul - Aprendizagem",
        "description": "Placa padrão Mercosul para veículos de autoescola",
        "country": "BR",
        "category": "aprendizagem",
        "format_pattern": "AAA9A99",
        "format_example": "ABC1D23",
        "plate_color_name": "Branca com faixa vermelha",
        "background_color_hex": "#FFFFFF",
        "text_color_hex": "#000000",
    },
    {
        "code": "BR_MERCOSUL_OFICIAL",
        "name": "Mercosul - Oficial",
        "description": "Placa padrão Mercosul para veículos oficiais do governo",
        "country": "BR",
        "category": "oficial",
        "format_pattern": "AAA9A99",
        "format_example": "ABC1D23",
        "plate_color_name": "Branca com faixa verde",
        "background_color_hex": "#FFFFFF",
        "text_color_hex": "#000000",
    },
    {
        "code": "BR_MERCOSUL_DIPLOMATICO",
        "name": "Mercosul - Diplomático",
        "description": "Placa padrão Mercosul para veículos do corpo diplomático",
        "country": "BR",
        "category": "diplomatico",
        "format_pattern": "AAA9A99",
        "format_example": "ABC1D23",
        "plate_color_name": "Branca com faixa cinza",
        "background_color_hex": "#FFFFFF",
        "text_color_hex": "#000000",
    },

    # ===== SISTEMA ANTIGO (Até 2018) =====
    {
        "code": "BR_ANTIGA_PARTICULAR",
        "name": "Antiga - Particular (Cinza)",
        "description": "Placa antiga brasileira para veículos particulares (até 2018)",
        "country": "BR",
        "category": "particular",
        "format_pattern": "AAA-9999",
        "format_example": "ABC-1234",
        "plate_color_name": "Cinza",
        "background_color_hex": "#808080",
        "text_color_hex": "#000000",
    },
    {
        "code": "BR_ANTIGA_COMERCIAL",
        "name": "Antiga - Comercial/Aluguel (Vermelha)",
        "description": "Placa antiga brasileira para veículos comerciais e de aluguel",
        "country": "BR",
        "category": "comercial",
        "format_pattern": "AAA-9999",
        "format_example": "ABC-1234",
        "plate_color_name": "Vermelha",
        "background_color_hex": "#FF0000",
        "text_color_hex": "#FFFFFF",
    },
    {
        "code": "BR_ANTIGA_OFICIAL",
        "name": "Antiga - Oficial (Azul)",
        "description": "Placa antiga brasileira para veículos oficiais do governo",
        "country": "BR",
        "category": "oficial",
        "format_pattern": "AAA-9999",
        "format_example": "ABC-1234",
        "plate_color_name": "Azul",
        "background_color_hex": "#0000FF",
        "text_color_hex": "#FFFFFF",
    },
    {
        "code": "BR_ANTIGA_COLECAO",
        "name": "Antiga - Coleção/Histórico (Preta)",
        "description": "Placa antiga brasileira para veículos de coleção e históricos",
        "country": "BR",
        "category": "colecao",
        "format_pattern": "AAA-9999",
        "format_example": "ABC-1234",
        "plate_color_name": "Preta",
        "background_color_hex": "#000000",
        "text_color_hex": "#FFFFFF",
    },
    {
        "code": "BR_ANTIGA_APRENDIZAGEM",
        "name": "Antiga - Aprendizagem (Branca)",
        "description": "Placa antiga brasileira para veículos de autoescola",
        "country": "BR",
        "category": "aprendizagem",
        "format_pattern": "AAA-9999",
        "format_example": "ABC-1234",
        "plate_color_name": "Branca com letras vermelhas",
        "background_color_hex": "#FFFFFF",
        "text_color_hex": "#FF0000",
    },
]


def populate_plate_types():
    """Popular tipos de placas do Brasil"""
    db = SessionLocal()

    try:
        print("Populando tipos de placas brasileiras...")

        # Verificar quantos já existem
        existing_count = db.query(PlateType).count()
        print(f"Tipos de placas existentes: {existing_count}")

        created_count = 0
        skipped_count = 0

        for plate_data in PLATE_TYPES_BR:
            # Verificar se já existe pelo código
            existing = db.query(PlateType).filter(PlateType.code == plate_data["code"]).first()

            if existing:
                print(f"✓ Já existe: {plate_data['name']}")
                skipped_count += 1
                continue

            # Criar novo tipo de placa
            plate_type = PlateType(
                id=uuid.uuid4(),
                **plate_data,
                active=True
            )
            db.add(plate_type)
            print(f"+ Criado: {plate_data['name']}")
            created_count += 1

        db.commit()

        print(f"\n✅ Concluído!")
        print(f"   Criados: {created_count}")
        print(f"   Ignorados (já existiam): {skipped_count}")
        print(f"   Total no banco: {db.query(PlateType).count()}")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    populate_plate_types()
