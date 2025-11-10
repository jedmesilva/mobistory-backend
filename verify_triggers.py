"""
Script de verificação dos triggers criados
"""
from sqlalchemy import text
from app.core.database import engine


def verify_triggers():
    """Verifica se todos os triggers foram criados"""

    with engine.connect() as conn:
        print("=" * 80)
        print("VERIFICAÇÃO DOS TRIGGERS DE VEHICLE_EVENTS")
        print("=" * 80)

        # 1. Verificar função helper
        print("\n1. Verificando função helper...")
        result = conn.execute(text("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
              AND routine_name = 'create_vehicle_event'
        """))
        helper = result.fetchone()

        if helper:
            print(f"   [OK] Função helper: {helper[0]}")
        else:
            print("   [ERRO] Função helper não encontrada")

        # 2. Verificar funções trigger
        print("\n2. Verificando funções trigger...")
        expected_functions = [
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

        result = conn.execute(text("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
              AND routine_name LIKE 'trigger_%_event'
            ORDER BY routine_name
        """))
        functions = [row[0] for row in result.fetchall()]

        print(f"   Total de funções trigger: {len(functions)}")
        for func in functions:
            print(f"   - {func}")

        missing = set(expected_functions) - set(functions)
        if missing:
            print(f"   [AVISO] Funções faltando: {missing}")
        else:
            print(f"   [OK] Todas as {len(expected_functions)} funções criadas")

        # 3. Verificar triggers
        print("\n3. Verificando triggers...")
        expected_triggers = [
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

        result = conn.execute(text("""
            SELECT
                trigger_name,
                event_object_table,
                action_timing,
                event_manipulation
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
              AND trigger_name LIKE 'trg_%_event'
            ORDER BY trigger_name
        """))
        triggers = result.fetchall()

        print(f"   Total de triggers: {len(triggers)}")
        for trg in triggers:
            print(f"   - {trg[0]} em {trg[1]} ({trg[2]} {trg[3]})")

        trigger_names = [(trg[0], trg[1]) for trg in triggers]
        missing_trg = set(expected_triggers) - set(trigger_names)
        if missing_trg:
            print(f"   [AVISO] Triggers faltando: {missing_trg}")
        else:
            print(f"   [OK] Todos os {len(expected_triggers)} triggers criados")

        # 4. Resumo por categoria
        print("\n4. Resumo por categoria de evento:")
        categories = {
            'usage': ['vehicle_refuels', 'mileage_records'],
            'modification': ['plates', 'links', 'vehicle_colors', 'vehicle_covers'],
            'maintenance': ['odometers'],
            'alert': ['vehicle_claims'],
            'documentation': ['actions']
        }

        for category, tables in categories.items():
            print(f"\n   {category.upper()}:")
            for table in tables:
                has_trigger = any(trg[1] == table for trg in triggers)
                status = "[OK]" if has_trigger else "[FALTA]"
                print(f"      {status} {table}")

        print("\n" + "=" * 80)
        print("VERIFICAÇÃO CONCLUÍDA")
        print("=" * 80)
        print(f"\nResultado: {len(functions)}/9 funções, {len(triggers)}/9 triggers")


if __name__ == "__main__":
    verify_triggers()
