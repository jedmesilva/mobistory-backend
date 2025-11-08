"""
Endpoint para moments com detalhes completos
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()


@router.get("/moments-with-details")
def get_moments_with_details(db: Session = Depends(get_db)):
    """Retorna todos os momentos com detalhes completos (vehicle, entity, images, reactions, comments)"""
    query = text("""
        SELECT
            mo.*,
            json_build_object(
                'id', v.id,
                'brand_id', v.brand_id,
                'model_id', v.model_id,
                'version_id', v.version_id,
                'category_id', v.category_id,
                'chassis', v.chassis,
                'model_year', v.model_year,
                'manufacture_year', v.manufacture_year,
                'active', v.active,
                'created_at', v.created_at,
                'updated_at', v.updated_at,
                'brands', json_build_object(
                    'id', b.id,
                    'brand', b.brand
                ),
                'models', json_build_object(
                    'id', md.id,
                    'model', md.model
                ),
                'model_versions', CASE
                    WHEN mv.id IS NOT NULL THEN json_build_object(
                        'id', mv.id,
                        'version', mv.version
                    )
                    ELSE NULL
                END,
                'plates', COALESCE(
                    (SELECT json_agg(json_build_object(
                        'id', p.id,
                        'plate', p.plate,
                        'state', p.state,
                        'active', p.active
                    ))
                    FROM plates p
                    WHERE p.vehicle_id = v.id AND p.active = true),
                    '[]'::json
                ),
                'colors', COALESCE(
                    (SELECT json_agg(json_build_object(
                        'id', c.id,
                        'color', c.color,
                        'active', c.active
                    ))
                    FROM colors c
                    WHERE c.vehicle_id = v.id AND c.active = true),
                    '[]'::json
                ),
                'vehicle_images', COALESCE(
                    (SELECT json_agg(json_build_object(
                        'id', vi.id,
                        'image_url', vi.image_url,
                        'is_primary', vi.is_primary,
                        'width', vi.width,
                        'height', vi.height
                    ))
                    FROM vehicle_images vi
                    WHERE vi.vehicle_id = v.id),
                    '[]'::json
                )
            ) as vehicles,
            json_build_object(
                'id', e.id,
                'entity_type', e.entity_type,
                'name', en.name_value,
                'email', ec_email.contact_value
            ) as entities,
            COALESCE(
                (SELECT json_agg(json_build_object(
                    'id', mi.id,
                    'image_url', mi.image_url,
                    'image_order', mi.image_order,
                    'width', mi.width,
                    'height', mi.height
                ) ORDER BY mi.image_order)
                FROM moment_images mi
                WHERE mi.moment_id = mo.id),
                '[]'::json
            ) as moment_images,
            COALESCE(
                (SELECT json_agg(json_build_object(
                    'id', mr.id,
                    'reaction_type', mr.reaction_type,
                    'entities', json_build_object(
                        'id', er.id,
                        'name', ern.name_value
                    )
                ))
                FROM moment_reactions mr
                LEFT JOIN entities er ON mr.entity_id = er.id
                LEFT JOIN entity_names ern ON er.primary_name_id = ern.id
                WHERE mr.moment_id = mo.id),
                '[]'::json
            ) as moment_reactions,
            COALESCE(
                (SELECT json_agg(json_build_object(
                    'id', mc.id,
                    'comment', mc.comment,
                    'parent_comment_id', mc.parent_comment_id,
                    'created_at', mc.created_at,
                    'entities', json_build_object(
                        'id', ecc.id,
                        'name', eccn.name_value
                    )
                ) ORDER BY mc.created_at)
                FROM moment_comments mc
                LEFT JOIN entities ecc ON mc.entity_id = ecc.id
                LEFT JOIN entity_names eccn ON ecc.primary_name_id = eccn.id
                WHERE mc.moment_id = mo.id),
                '[]'::json
            ) as moment_comments
        FROM moments mo
        LEFT JOIN vehicles v ON mo.vehicle_id = v.id
        LEFT JOIN brands b ON v.brand_id = b.id
        LEFT JOIN models md ON v.model_id = md.id
        LEFT JOIN model_versions mv ON v.version_id = mv.id
        LEFT JOIN entities e ON mo.entity_id = e.id
        LEFT JOIN entity_names en ON e.primary_name_id = en.id
        LEFT JOIN entity_contacts ec_email ON e.primary_email_contact_id = ec_email.id
        WHERE mo.active = true
        ORDER BY mo.created_at DESC
    """)

    result = db.execute(query)
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]
