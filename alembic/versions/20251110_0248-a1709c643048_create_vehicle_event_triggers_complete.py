"""create_vehicle_event_triggers_complete

Revision ID: a1709c643048
Revises: 5b2fdb8cbbee
Create Date: 2025-11-10 02:48:37.421697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1709c643048'
down_revision = '5b2fdb8cbbee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Cria triggers automáticos para geração de eventos em vehicle_events.

    Implementa 9 triggers para as seguintes tabelas:
    - vehicle_refuels (abastecimentos)
    - mileage_records (quilometragem)
    - vehicle_claims (sinistros)
    - plates (placas)
    - links (vínculos)
    - odometers (odômetros)
    - vehicle_colors (cores)
    - vehicle_covers (fotos)
    - actions (ações)
    """

    # ========================================================================
    # 1. FUNÇÃO HELPER REUTILIZÁVEL
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.create_vehicle_event(
            p_vehicle_id UUID,
            p_entity_id UUID,
            p_category VARCHAR(50),
            p_type VARCHAR(100),
            p_timestamp TIMESTAMP WITH TIME ZONE,
            p_title VARCHAR(200),
            p_description TEXT,
            p_event_data JSONB,
            p_source_table VARCHAR(100),
            p_source_record_id UUID,
            p_severity VARCHAR(20) DEFAULT NULL,
            p_tags JSONB DEFAULT NULL,
            p_is_public VARCHAR(20) DEFAULT 'owner_only'
        )
        RETURNS UUID
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_id UUID;
        BEGIN
            -- Verificar se evento já existe (idempotência)
            SELECT id INTO v_event_id
            FROM public.vehicle_events
            WHERE source_table = p_source_table
              AND source_record_id = p_source_record_id
            LIMIT 1;

            IF v_event_id IS NOT NULL THEN
                RETURN v_event_id;  -- Evento já existe
            END IF;

            -- Criar novo evento
            INSERT INTO public.vehicle_events (
                vehicle_id, entity_id, event_category, event_type,
                event_timestamp, title, description, event_data,
                source_table, source_record_id, severity, tags, is_public
            ) VALUES (
                p_vehicle_id, p_entity_id, p_category, p_type,
                p_timestamp, p_title, p_description, p_event_data,
                p_source_table, p_source_record_id, p_severity, p_tags, p_is_public
            )
            RETURNING id INTO v_event_id;

            RETURN v_event_id;
        END;
        $$;
    """)

    # ========================================================================
    # 2. TRIGGER: vehicle_refuels (ABASTECIMENTOS)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_vehicle_refuel_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
        BEGIN
            v_title := 'Abastecimento: ' || COALESCE(NEW.quantity::TEXT, '0') || 'L';

            v_event_data := jsonb_build_object(
                'liters', NEW.quantity,
                'price_per_liter', NEW.unit_price,
                'total_price', NEW.total_price,
                'odometer_reading', NEW.refuel_km,
                'full_tank', NEW.full_tank,
                'observations', NEW.observations
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NEW.registered_by_entity_id,
                p_category := 'usage',
                p_type := 'refuel',
                p_timestamp := NEW.refuel_date,
                p_title := v_title,
                p_description := 'Abastecimento registrado',
                p_event_data := v_event_data,
                p_source_table := 'vehicle_refuels',
                p_source_record_id := NEW.id,
                p_tags := jsonb_build_array('abastecimento', 'combustível')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_vehicle_refuel_event
            AFTER INSERT ON public.vehicle_refuels
            FOR EACH ROW
            EXECUTE FUNCTION public.trigger_vehicle_refuel_event();
    """)

    # ========================================================================
    # 3. TRIGGER: mileage_records (QUILOMETRAGEM)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_mileage_record_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
            v_previous_mileage INTEGER;
        BEGIN
            -- Buscar quilometragem anterior
            SELECT mileage INTO v_previous_mileage
            FROM public.mileage_records
            WHERE vehicle_id = NEW.vehicle_id
              AND id != NEW.id
            ORDER BY recorded_at DESC
            LIMIT 1;

            v_title := 'Quilometragem atualizada: ' || NEW.mileage || ' km';

            v_event_data := jsonb_build_object(
                'mileage', NEW.mileage,
                'odometer_id', NEW.odometer_id,
                'previous_mileage', v_previous_mileage,
                'difference', NEW.mileage - COALESCE(v_previous_mileage, 0)
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NULL,  -- Buscar de registered_by_link_id se necessário
                p_category := 'usage',
                p_type := 'mileage_update',
                p_timestamp := NEW.recorded_at,
                p_title := v_title,
                p_description := 'Registro de quilometragem',
                p_event_data := v_event_data,
                p_source_table := 'mileage_records',
                p_source_record_id := NEW.id,
                p_tags := jsonb_build_array('quilometragem', 'odometro')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_mileage_record_event
            AFTER INSERT ON public.mileage_records
            FOR EACH ROW
            EXECUTE FUNCTION public.trigger_mileage_record_event();
    """)

    # ========================================================================
    # 4. TRIGGER: vehicle_claims (SINISTROS - CRÍTICO)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_vehicle_claim_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
            v_severity VARCHAR(20);
        BEGIN
            v_title := 'Sinistro: ' || COALESCE(NEW.claim_type, 'não especificado');

            -- Mapear severidade
            v_severity := CASE NEW.severity
                WHEN 'minor' THEN 'warning'
                WHEN 'moderate' THEN 'error'
                WHEN 'severe' THEN 'critical'
                WHEN 'total_loss' THEN 'critical'
                ELSE 'warning'
            END;

            v_event_data := jsonb_build_object(
                'claim_type', NEW.claim_type,
                'severity', NEW.severity,
                'claim_km', NEW.claim_km,
                'location', jsonb_build_object(
                    'lat', NEW.location_lat,
                    'lng', NEW.location_lng,
                    'address', NEW.address
                ),
                'police_report', NEW.police_report,
                'insurance_status', NEW.insurance_status,
                'total_repair_cost', NEW.total_repair_cost,
                'status', NEW.status,
                'description', NEW.description
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NULL,  -- Buscar de link_id se necessário
                p_category := 'alert',
                p_type := 'claim_reported',
                p_timestamp := NEW.claim_date,
                p_title := v_title,
                p_description := COALESCE(NEW.description, 'Sinistro registrado'),
                p_event_data := v_event_data,
                p_source_table := 'vehicle_claims',
                p_source_record_id := NEW.id,
                p_severity := v_severity,
                p_tags := jsonb_build_array('sinistro', 'acidente', NEW.claim_type)
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_vehicle_claim_event
            AFTER INSERT OR UPDATE ON public.vehicle_claims
            FOR EACH ROW
            EXECUTE FUNCTION public.trigger_vehicle_claim_event();
    """)

    # ========================================================================
    # 5. TRIGGER: plates (PLACAS)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_plate_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
            v_event_type VARCHAR(100);
        BEGIN
            -- Filtrar: só gerar evento se for INSERT com status ACTIVE
            -- ou UPDATE com mudança de status
            IF TG_OP = 'INSERT' THEN
                IF NEW.status != 'ACTIVE' THEN
                    RETURN NEW;  -- Não gerar evento
                END IF;
                v_event_type := 'plate_added';
                v_title := 'Placa adicionada: ' || NEW.plate_number;
            ELSIF TG_OP = 'UPDATE' THEN
                IF OLD.status = NEW.status THEN
                    RETURN NEW;  -- Não houve mudança de status
                END IF;
                v_event_type := 'plate_changed';
                v_title := 'Placa alterada: ' || NEW.plate_number;
            ELSE
                RETURN NEW;  -- DELETE não gera evento
            END IF;

            v_event_data := jsonb_build_object(
                'plate_number', NEW.plate_number,
                'state', NEW.state,
                'city', NEW.city,
                'licensing_start_date', NEW.licensing_start_date,
                'licensing_end_date', NEW.licensing_end_date,
                'status', NEW.status
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NEW.created_by_entity_id,
                p_category := 'modification',
                p_type := v_event_type,
                p_timestamp := COALESCE(NEW.licensing_start_date::TIMESTAMP WITH TIME ZONE, NOW()),
                p_title := v_title,
                p_description := 'Alteração de placa do veículo',
                p_event_data := v_event_data,
                p_source_table := 'plates',
                p_source_record_id := NEW.id,
                p_tags := jsonb_build_array('placa', 'documentação')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_plate_event
            AFTER INSERT OR UPDATE ON public.plates
            FOR EACH ROW
            EXECUTE FUNCTION public.trigger_plate_event();
    """)

    # ========================================================================
    # 6. TRIGGER: links (VÍNCULOS)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_link_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
            v_event_type VARCHAR(100);
            v_severity VARCHAR(20);
        BEGIN
            IF TG_OP = 'INSERT' THEN
                v_event_type := 'link_created';
                v_title := 'Vínculo criado';
                v_severity := 'info';
            ELSIF OLD.status != NEW.status THEN
                v_event_type := 'link_status_changed';
                v_title := 'Status do vínculo alterado: ' || OLD.status || ' → ' || NEW.status;
                v_severity := CASE NEW.status
                    WHEN 'suspended' THEN 'warning'
                    WHEN 'terminated' THEN 'error'
                    ELSE 'info'
                END;
            ELSIF NEW.end_date IS NOT NULL AND OLD.end_date IS NULL THEN
                v_event_type := 'link_terminated';
                v_title := 'Vínculo terminado';
                v_severity := 'warning';
            ELSE
                RETURN NEW;  -- Não gerar evento para outras alterações
            END IF;

            v_event_data := jsonb_build_object(
                'link_code', NEW.link_code,
                'entity_id', NEW.entity_id,
                'link_type_id', NEW.link_type_id,
                'status', NEW.status,
                'previous_status', OLD.status,
                'start_date', NEW.start_date,
                'end_date', NEW.end_date
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NEW.entity_id,
                p_category := 'modification',
                p_type := v_event_type,
                p_timestamp := COALESCE(NEW.updated_at, NOW()),
                p_title := v_title,
                p_description := 'Alteração em vínculo de entidade',
                p_event_data := v_event_data,
                p_source_table := 'links',
                p_source_record_id := NEW.id,
                p_severity := v_severity,
                p_tags := jsonb_build_array('vínculo', 'acesso')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_link_event
            AFTER INSERT OR UPDATE ON public.links
            FOR EACH ROW
            EXECUTE FUNCTION public.trigger_link_event();
    """)

    # ========================================================================
    # 7. TRIGGER: odometers (ODÔMETROS)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_odometer_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
            v_event_type VARCHAR(100);
            v_severity VARCHAR(20);
        BEGIN
            IF TG_OP = 'INSERT' THEN
                v_event_type := 'odometer_installed';
                v_title := 'Odômetro instalado: ' || COALESCE(NEW.brand, '') || ' ' || COALESCE(NEW.model, '');
                v_severity := CASE
                    WHEN NEW.damage_type IS NOT NULL THEN 'warning'
                    ELSE NULL
                END;
            ELSIF NEW.removal_date IS NOT NULL AND OLD.removal_date IS NULL THEN
                v_event_type := 'odometer_removed';
                v_title := 'Odômetro removido';
                v_severity := 'info';
            ELSE
                RETURN NEW;
            END IF;

            v_event_data := jsonb_build_object(
                'brand', NEW.brand,
                'model', NEW.model,
                'part_number', NEW.part_number,
                'installation_date', NEW.installation_date,
                'removal_date', NEW.removal_date,
                'cost', NEW.cost,
                'warranty_months', NEW.warranty_months,
                'reason_for_change', NEW.reason_for_change,
                'damage_type', NEW.damage_type
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NULL,
                p_category := 'maintenance',
                p_type := v_event_type,
                p_timestamp := COALESCE(NEW.installation_date::TIMESTAMP WITH TIME ZONE,
                                       NEW.removal_date::TIMESTAMP WITH TIME ZONE,
                                       NOW()),
                p_title := v_title,
                p_description := COALESCE(NEW.reason_for_change, 'Manutenção de odômetro'),
                p_event_data := v_event_data,
                p_source_table := 'odometers',
                p_source_record_id := NEW.id,
                p_severity := v_severity,
                p_tags := jsonb_build_array('odômetro', 'manutenção')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_odometer_event
            AFTER INSERT OR UPDATE ON public.odometers
            FOR EACH ROW
            EXECUTE FUNCTION public.trigger_odometer_event();
    """)

    # ========================================================================
    # 8. TRIGGER: vehicle_colors (CORES)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_vehicle_color_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
            v_color_name VARCHAR;
        BEGIN
            -- Só gerar evento se for cor primária
            IF NEW.is_primary = FALSE THEN
                RETURN NEW;
            END IF;

            -- Buscar nome da cor
            SELECT name INTO v_color_name
            FROM public.colors
            WHERE id = NEW.color_id;

            v_title := 'Cor alterada para ' || COALESCE(v_color_name, 'cor não especificada');

            v_event_data := jsonb_build_object(
                'color_id', NEW.color_id,
                'color_name', v_color_name,
                'is_primary', NEW.is_primary
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NULL,
                p_category := 'modification',
                p_type := 'color_change',
                p_timestamp := COALESCE(NEW.created_at, NOW()),
                p_title := v_title,
                p_description := 'Alteração de cor do veículo',
                p_event_data := v_event_data,
                p_source_table := 'vehicle_colors',
                p_source_record_id := NEW.id,
                p_tags := jsonb_build_array('cor', 'personalização')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_vehicle_color_event
            AFTER INSERT OR UPDATE ON public.vehicle_colors
            FOR EACH ROW
            WHEN (NEW.is_primary = TRUE)
            EXECUTE FUNCTION public.trigger_vehicle_color_event();
    """)

    # ========================================================================
    # 9. TRIGGER: vehicle_covers (FOTOS/CAPAS)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_vehicle_cover_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
            v_file_url TEXT;
        BEGIN
            -- Só gerar evento se for capa primária
            IF NEW.is_primary = FALSE THEN
                RETURN NEW;
            END IF;

            -- Buscar URL do arquivo
            SELECT file_url INTO v_file_url
            FROM public.files
            WHERE id = NEW.file_id;

            v_title := 'Foto de capa atualizada';

            v_event_data := jsonb_build_object(
                'file_id', NEW.file_id,
                'file_url', v_file_url,
                'is_primary', NEW.is_primary,
                'display_order', NEW.display_order
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NULL,
                p_category := 'modification',
                p_type := 'cover_changed',
                p_timestamp := COALESCE(NEW.created_at, NOW()),
                p_title := v_title,
                p_description := 'Imagem de capa do veículo alterada',
                p_event_data := v_event_data,
                p_source_table := 'vehicle_covers',
                p_source_record_id := NEW.id,
                p_tags := jsonb_build_array('foto', 'capa', 'visual')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_vehicle_cover_event
            AFTER INSERT OR UPDATE ON public.vehicle_covers
            FOR EACH ROW
            WHEN (NEW.is_primary = TRUE)
            EXECUTE FUNCTION public.trigger_vehicle_cover_event();
    """)

    # ========================================================================
    # 10. TRIGGER: actions (AÇÕES EXECUTADAS)
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.trigger_action_event()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_event_data JSONB;
            v_title VARCHAR(200);
        BEGIN
            -- Só gerar evento quando ação for concluída
            IF NEW.status != 'completed' OR OLD.status = 'completed' THEN
                RETURN NEW;
            END IF;

            v_title := 'Ação executada: ' || COALESCE(NEW.title, 'sem título');

            v_event_data := jsonb_build_object(
                'action_type_id', NEW.action_type_id,
                'title', NEW.title,
                'description', NEW.description,
                'status', NEW.status,
                'priority', NEW.priority,
                'scheduled_for', NEW.scheduled_for,
                'executed_at', NEW.executed_at,
                'executed_by_entity_id', NEW.executed_by_entity_id
            );

            PERFORM public.create_vehicle_event(
                p_vehicle_id := NEW.vehicle_id,
                p_entity_id := NEW.executed_by_entity_id,
                p_category := 'documentation',
                p_type := 'action_executed',
                p_timestamp := COALESCE(NEW.executed_at, NOW()),
                p_title := v_title,
                p_description := COALESCE(NEW.description, 'Ação concluída'),
                p_event_data := v_event_data,
                p_source_table := 'actions',
                p_source_record_id := NEW.id,
                p_tags := jsonb_build_array('ação', 'tarefa')
            );

            RETURN NEW;
        END;
        $$;

        CREATE TRIGGER trg_action_event
            AFTER UPDATE ON public.actions
            FOR EACH ROW
            WHEN (NEW.status = 'completed' AND OLD.status != 'completed')
            EXECUTE FUNCTION public.trigger_action_event();
    """)


def downgrade() -> None:
    """
    Remove todos os triggers e a função helper.
    """

    # Remover triggers
    triggers = [
        ('trg_vehicle_refuel_event', 'vehicle_refuels'),
        ('trg_mileage_record_event', 'mileage_records'),
        ('trg_vehicle_claim_event', 'vehicle_claims'),
        ('trg_plate_event', 'plates'),
        ('trg_link_event', 'links'),
        ('trg_odometer_event', 'odometers'),
        ('trg_vehicle_color_event', 'vehicle_colors'),
        ('trg_vehicle_cover_event', 'vehicle_covers'),
        ('trg_action_event', 'actions'),
    ]

    for trigger_name, table_name in triggers:
        op.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON public.{table_name}")

    # Remover funções trigger
    functions = [
        'trigger_vehicle_refuel_event',
        'trigger_mileage_record_event',
        'trigger_vehicle_claim_event',
        'trigger_plate_event',
        'trigger_link_event',
        'trigger_odometer_event',
        'trigger_vehicle_color_event',
        'trigger_vehicle_cover_event',
        'trigger_action_event',
    ]

    for function_name in functions:
        op.execute(f"DROP FUNCTION IF EXISTS public.{function_name}()")

    # Remover função helper
    op.execute("DROP FUNCTION IF EXISTS public.create_vehicle_event")
