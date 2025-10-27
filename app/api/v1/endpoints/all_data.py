"""
Endpoints para servir TODOS os dados (igual ao Supabase)
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db
from typing import List

router = APIRouter()


@router.get("/vehicles")
def get_vehicles(db: Session = Depends(get_db)):
    """Retorna todos os veículos"""
    result = db.execute(text("SELECT * FROM vehicles WHERE active = true"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Retorna um veículo específico"""
    result = db.execute(text("SELECT * FROM vehicles WHERE id = :id"), {"id": vehicle_id})
    columns = result.keys()
    row = result.fetchone()
    if row:
        return dict(zip(columns, row))
    return {"error": "Vehicle not found"}


@router.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    """Retorna todas as marcas"""
    result = db.execute(text("SELECT * FROM brands WHERE active = true"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/models")
def get_models(db: Session = Depends(get_db)):
    """Retorna todos os modelos"""
    result = db.execute(text("SELECT * FROM models WHERE active = true"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/model_versions")
def get_model_versions(db: Session = Depends(get_db)):
    """Retorna todas as versões"""
    result = db.execute(text("SELECT * FROM model_versions WHERE active = true"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/colors")
def get_colors(db: Session = Depends(get_db)):
    """Retorna todas as cores"""
    result = db.execute(text("SELECT * FROM colors"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/plates")
def get_plates(db: Session = Depends(get_db)):
    """Retorna todas as placas"""
    result = db.execute(text("SELECT * FROM plates WHERE active = true"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/entities")
def get_entities(db: Session = Depends(get_db)):
    """Retorna todas as entidades"""
    result = db.execute(text("SELECT * FROM entities WHERE active = true"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/entities/{entity_id}")
def get_entity(entity_id: str, db: Session = Depends(get_db)):
    """Retorna uma entidade específica"""
    result = db.execute(text("SELECT * FROM entities WHERE id = :id"), {"id": entity_id})
    columns = result.keys()
    row = result.fetchone()
    if row:
        return dict(zip(columns, row))
    return {"error": "Entity not found"}


@router.get("/conversations")
def get_conversations(db: Session = Depends(get_db)):
    """Retorna todas as conversas"""
    result = db.execute(text("SELECT * FROM conversations WHERE active = true ORDER BY last_message_at DESC"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Retorna uma conversa específica"""
    result = db.execute(text("SELECT * FROM conversations WHERE id = :id"), {"id": conversation_id})
    columns = result.keys()
    row = result.fetchone()
    if row:
        return dict(zip(columns, row))
    return {"error": "Conversation not found"}


@router.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    """Retorna mensagens de uma conversa"""
    result = db.execute(
        "SELECT * FROM messages WHERE conversation_id = :conv_id AND deleted = false ORDER BY created_at ASC",
        {"conv_id": conversation_id}
    )
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/moments")
def get_moments(db: Session = Depends(get_db)):
    """Retorna todos os momentos"""
    result = db.execute(text("SELECT * FROM moments WHERE active = true ORDER BY created_at DESC"))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/moments/{moment_id}")
def get_moment(moment_id: str, db: Session = Depends(get_db)):
    """Retorna um momento específico"""
    result = db.execute(text("SELECT * FROM moments WHERE id = :id"), {"id": moment_id})
    columns = result.keys()
    row = result.fetchone()
    if row:
        return dict(zip(columns, row))
    return {"error": "Moment not found"}


@router.get("/vehicles-with-details")
def get_vehicles_with_details(db: Session = Depends(get_db)):
    """Retorna todos os veiculos com detalhes (brands, models, plates, colors, fuels)"""
    query = text("""
        SELECT 
            v.*,
            json_build_object(
                'id', b.id,
                'brand', b.brand
            ) as brands,
            json_build_object(
                'id', m.id,
                'model', m.model
            ) as models,
            json_build_object(
                'id', mv.id,
                'version', mv.version
            ) as model_versions,
            json_build_object(
                'id', vc.id,
                'category', vc.category
            ) as vehicle_categories,
            COALESCE(
                json_agg(DISTINCT jsonb_build_object(
                    'id', p.id,
                    'plate', p.plate,
                    'state', p.state,
                    'active', p.active
                )) FILTER (WHERE p.id IS NOT NULL),
                '[]'::json
            ) as plates,
            COALESCE(
                json_agg(DISTINCT jsonb_build_object(
                    'id', c.id,
                    'color', c.color,
                    'active', c.active
                )) FILTER (WHERE c.id IS NOT NULL),
                '[]'::json
            ) as colors,
            COALESCE(
                json_agg(DISTINCT jsonb_build_object(
                    'id', vf.id,
                    'active', vf.active,
                    'fuels', jsonb_build_object(
                        'id', f.id,
                        'name', f.name,
                        'type', f.type
                    )
                )) FILTER (WHERE vf.id IS NOT NULL),
                '[]'::json
            ) as vehicle_fuels
        FROM vehicles v
        LEFT JOIN brands b ON v.brand_id = b.id
        LEFT JOIN models m ON v.model_id = m.id
        LEFT JOIN model_versions mv ON v.version_id = mv.id
        LEFT JOIN vehicle_categories vc ON v.category_id = vc.id
        LEFT JOIN plates p ON v.id = p.vehicle_id AND p.active = true
        LEFT JOIN colors c ON v.id = c.vehicle_id AND c.active = true
        LEFT JOIN vehicle_fuels vf ON v.id = vf.vehicle_id AND vf.active = true
        LEFT JOIN fuels f ON vf.fuel_id = f.id
        WHERE v.active = true
        GROUP BY v.id, b.id, b.brand, m.id, m.model, mv.id, mv.version, vc.id, vc.category
        ORDER BY v.created_at DESC
    """)
    
    result = db.execute(query)
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


@router.get("/vehicles-with-details/{vehicle_id}")
def get_vehicle_with_details(vehicle_id: str, db: Session = Depends(get_db)):
    """Retorna um veículo específico com todos os detalhes (brands, models, plates, colors, fuels, entity links)"""
    query = text("""
        SELECT
            v.*,
            json_build_object(
                'id', b.id,
                'brand', b.brand
            ) as brands,
            json_build_object(
                'id', m.id,
                'model', m.model
            ) as models,
            json_build_object(
                'id', mv.id,
                'version', mv.version
            ) as model_versions,
            json_build_object(
                'id', vc.id,
                'category', vc.category
            ) as vehicle_categories,
            COALESCE(
                json_agg(DISTINCT jsonb_build_object(
                    'id', p.id,
                    'plate', p.plate,
                    'state', p.state,
                    'active', p.active
                )) FILTER (WHERE p.id IS NOT NULL),
                '[]'::json
            ) as plates,
            COALESCE(
                json_agg(DISTINCT jsonb_build_object(
                    'id', c.id,
                    'color', c.color,
                    'active', c.active
                )) FILTER (WHERE c.id IS NOT NULL),
                '[]'::json
            ) as colors,
            COALESCE(
                json_agg(DISTINCT jsonb_build_object(
                    'id', vf.id,
                    'active', vf.active,
                    'fuels', jsonb_build_object(
                        'id', f.id,
                        'name', f.name,
                        'type', f.type
                    )
                )) FILTER (WHERE vf.id IS NOT NULL),
                '[]'::json
            ) as vehicle_fuels,
            COALESCE(
                json_agg(DISTINCT jsonb_build_object(
                    'id', vel.id,
                    'relationship_type', vel.relationship_type,
                    'status', vel.status,
                    'start_date', vel.start_date,
                    'end_date', vel.end_date,
                    'active', vel.active
                )) FILTER (WHERE vel.id IS NOT NULL),
                '[]'::json
            ) as vehicle_entity_links
        FROM vehicles v
        LEFT JOIN brands b ON v.brand_id = b.id
        LEFT JOIN models m ON v.model_id = m.id
        LEFT JOIN model_versions mv ON v.version_id = mv.id
        LEFT JOIN vehicle_categories vc ON v.category_id = vc.id
        LEFT JOIN plates p ON v.id = p.vehicle_id AND p.active = true
        LEFT JOIN colors c ON v.id = c.vehicle_id AND c.active = true
        LEFT JOIN vehicle_fuels vf ON v.id = vf.vehicle_id AND vf.active = true
        LEFT JOIN fuels f ON vf.fuel_id = f.id
        LEFT JOIN vehicle_entity_links vel ON v.id = vel.vehicle_id AND vel.active = true
        WHERE v.id = :vehicle_id AND v.active = true
        GROUP BY v.id, b.id, b.brand, m.id, m.model, mv.id, mv.version, vc.id, vc.category
    """)

    result = db.execute(query, {"vehicle_id": vehicle_id})
    columns = result.keys()
    row = result.fetchone()

    if row:
        return dict(zip(columns, row))

    return {"error": "Vehicle not found"}
