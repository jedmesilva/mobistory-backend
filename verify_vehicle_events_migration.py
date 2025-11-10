"""
Script de verificação da migration de vehicle_events
"""
from sqlalchemy import text
from app.core.database import engine


def verify_migration():
    """Verifica se a migration de vehicle_events foi executada corretamente"""

    with engine.connect() as conn:
        print("=" * 80)
        print("VERIFICAÇÃO DA MIGRATION DE VEHICLE_EVENTS")
        print("=" * 80)

        # 1. Verificar se a tabela principal foi criada
        print("\n1. Verificando tabela principal...")
        result = conn.execute(text("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'vehicle_events'
        """))
        table_info = result.fetchone()

        if table_info:
            print(f"   [OK] Tabela vehicle_events encontrada (tipo: {table_info[1]})")
        else:
            print("   [ERRO] Tabela vehicle_events não encontrada!")
            return

        # 2. Verificar colunas da tabela
        print("\n2. Verificando colunas...")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'vehicle_events'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        print(f"   Total de colunas: {len(columns)}")
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"   - {col[0]}: {col[1]} ({nullable})")

        expected_columns = [
            'id', 'vehicle_id', 'entity_id', 'event_category', 'event_type',
            'event_timestamp', 'severity', 'title', 'description', 'event_data',
            'source_table', 'source_record_id', 'tags', 'metadata', 'is_public',
            'created_at', 'updated_at'
        ]

        column_names = [col[0] for col in columns]
        missing = set(expected_columns) - set(column_names)
        if missing:
            print(f"   [AVISO] Colunas faltando: {missing}")
        else:
            print("   [OK] Todas as colunas esperadas estão presentes")

        # 3. Verificar partições criadas
        print("\n3. Verificando partições...")
        result = conn.execute(text("""
            SELECT
                child.relname as partition_name,
                pg_get_expr(child.relpartbound, child.oid) as partition_bounds
            FROM pg_inherits
            JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
            JOIN pg_class child ON pg_inherits.inhrelid = child.oid
            WHERE parent.relname = 'vehicle_events'
            ORDER BY child.relname
        """))
        partitions = result.fetchall()
        print(f"   Total de partições: {len(partitions)}")
        for part in partitions:
            print(f"   - {part[0]}: {part[1]}")

        expected_partitions = [
            'vehicle_events_2025_q1',
            'vehicle_events_2025_q2',
            'vehicle_events_2025_q3',
            'vehicle_events_2025_q4',
            'vehicle_events_2026_q1',
            'vehicle_events_2026_q2'
        ]

        partition_names = [part[0] for part in partitions]
        if len(partition_names) == len(expected_partitions):
            print("   [OK] Todas as 6 partições foram criadas")
        else:
            print(f"   [AVISO] Esperadas {len(expected_partitions)} partições, encontradas {len(partition_names)}")

        # 4. Verificar índices criados
        print("\n4. Verificando índices...")
        result = conn.execute(text("""
            SELECT
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND tablename = 'vehicle_events'
            ORDER BY indexname
        """))
        indexes = result.fetchall()
        print(f"   Total de índices: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx[0]}")

        expected_indexes = [
            'vehicle_events_pkey',
            'idx_vehicle_events_vehicle_timestamp',
            'idx_vehicle_events_category',
            'idx_vehicle_events_type',
            'idx_vehicle_events_entity',
            'idx_vehicle_events_source',
            'idx_vehicle_events_severity',
            'idx_vehicle_events_tags'
        ]

        index_names = [idx[0] for idx in indexes]

        # Verificar se todos os índices esperados estão presentes
        missing_indexes = []
        for expected in expected_indexes:
            found = any(expected in name for name in index_names)
            if not found:
                missing_indexes.append(expected)

        if missing_indexes:
            print(f"   [AVISO] Índices não encontrados: {missing_indexes}")
        else:
            print("   [OK] Todos os índices esperados foram criados")

        # 5. Verificar foreign keys
        print("\n5. Verificando foreign keys...")
        result = conn.execute(text("""
            SELECT
                conname as constraint_name,
                conrelid::regclass as table_name,
                confrelid::regclass as referenced_table
            FROM pg_constraint
            WHERE contype = 'f'
              AND conrelid = 'vehicle_events'::regclass
        """))
        fkeys = result.fetchall()
        print(f"   Total de foreign keys: {len(fkeys)}")
        for fk in fkeys:
            print(f"   - {fk[0]}: {fk[1]} -> {fk[2]}")

        if len(fkeys) >= 2:
            print("   [OK] Foreign keys criadas (vehicle_id, entity_id)")
        else:
            print("   [AVISO] Foreign keys faltando")

        # 6. Verificar função de criação de partições
        print("\n6. Verificando função create_vehicle_events_partition...")
        result = conn.execute(text("""
            SELECT
                routine_name,
                routine_type
            FROM information_schema.routines
            WHERE routine_schema = 'public'
              AND routine_name = 'create_vehicle_events_partition'
        """))
        function = result.fetchone()

        if function:
            print(f"   [OK] Função {function[0]} criada (tipo: {function[1]})")
        else:
            print("   [ERRO] Função create_vehicle_events_partition não encontrada")

        # 7. Testar inserção de um evento de exemplo (rollback)
        print("\n7. Testando inserção de evento...")
        try:
            trans = conn.begin()
            result = conn.execute(text("""
                INSERT INTO vehicle_events (
                    vehicle_id,
                    entity_id,
                    event_category,
                    event_type,
                    event_timestamp,
                    title,
                    event_data,
                    is_public
                )
                SELECT
                    v.id,
                    NULL,
                    'usage',
                    'test_event',
                    NOW(),
                    'Evento de teste da migration',
                    '{"test": true}'::jsonb,
                    'owner_only'
                FROM vehicles v
                LIMIT 1
                RETURNING id
            """))
            event_id = result.fetchone()

            if event_id:
                print(f"   [OK] Evento de teste inserido com sucesso (id: {event_id[0]})")

            trans.rollback()
            print("   [OK] Rollback executado - evento de teste removido")
        except Exception as e:
            print(f"   [ERRO] Falha no teste de inserção: {e}")

        print("\n" + "=" * 80)
        print("VERIFICAÇÃO CONCLUÍDA")
        print("=" * 80)


if __name__ == "__main__":
    verify_migration()
