"""
Script de verificação da migration de permissões
"""
from sqlalchemy import text
from app.core.database import engine


def verify_migration():
    """Verifica se a migration de permissões foi executada corretamente"""

    with engine.connect() as conn:
        print("=" * 80)
        print("VERIFICAÇÃO DA MIGRATION DE PERMISSÕES")
        print("=" * 80)

        # 1. Verificar se as tabelas foram criadas
        print("\n1. Verificando tabelas criadas...")
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('permissions', 'link_type_permissions')
            ORDER BY table_name
        """))
        tables = result.fetchall()
        print(f"   Tabelas encontradas: {[t[0] for t in tables]}")

        if len(tables) == 2:
            print("   [OK] Ambas as tabelas foram criadas")
        else:
            print("   [ERRO] Tabelas faltando!")
            return

        # 2. Verificar permissões criadas
        print("\n2. Verificando permissões...")
        result = conn.execute(text("""
            SELECT code, name, category
            FROM permissions
            ORDER BY category, code
        """))
        permissions = result.fetchall()
        print(f"   Total de permissões: {len(permissions)}")
        for perm in permissions:
            print(f"   - [{perm[2]}] {perm[0]}: {perm[1]}")

        if len(permissions) >= 6:
            print("   [OK] Permissões básicas criadas")
        else:
            print("   [AVISO]  Menos permissões que o esperado")

        # 3. Verificar link_types
        print("\n3. Verificando tipos de vínculos...")
        result = conn.execute(text("""
            SELECT code, name
            FROM link_types
            ORDER BY code
        """))
        link_types = result.fetchall()
        print(f"   Total de tipos: {len(link_types)}")
        for lt in link_types:
            print(f"   - {lt[0]}: {lt[1]}")

        # 4. Verificar permissões por tipo de vínculo
        print("\n4. Verificando permissões atribuídas aos tipos de vínculo...")
        result = conn.execute(text("""
            SELECT
                lt.code as link_type_code,
                lt.name as link_type_name,
                COUNT(ltp.permission_id) as total_permissions,
                STRING_AGG(p.code, ', ' ORDER BY p.code) as permissions
            FROM link_types lt
            LEFT JOIN link_type_permissions ltp ON ltp.link_type_id = lt.id
            LEFT JOIN permissions p ON p.id = ltp.permission_id
            GROUP BY lt.id, lt.code, lt.name
            ORDER BY total_permissions DESC, lt.code
        """))
        type_permissions = result.fetchall()

        for tp in type_permissions:
            print(f"\n   {tp[1]} ({tp[0]}):")
            print(f"   - Total: {tp[2]} permissões")
            print(f"   - Permissões: {tp[3] or 'Nenhuma'}")

        # 5. Verificar se coluna permissions foi removida de link_types
        print("\n5. Verificando se coluna 'permissions' foi removida de link_types...")
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'link_types'
              AND column_name = 'permissions'
        """))
        has_permissions_column = result.fetchone()

        if has_permissions_column:
            print("   [ERRO] Coluna 'permissions' ainda existe!")
        else:
            print("   [OK] Coluna 'permissions' foi removida")

        # 6. Verificar se função foi criada
        print("\n6. Verificando função check_link_permission...")
        result = conn.execute(text("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
              AND routine_name = 'check_link_permission'
        """))
        has_function = result.fetchone()

        if has_function:
            print("   [OK] Função check_link_permission criada")
        else:
            print("   [ERRO] Função check_link_permission não encontrada")

        # 7. Verificar índices
        print("\n7. Verificando índices...")
        result = conn.execute(text("""
            SELECT indexname, tablename
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND (tablename = 'permissions' OR tablename = 'link_type_permissions')
            ORDER BY tablename, indexname
        """))
        indexes = result.fetchall()
        print(f"   Total de índices: {len(indexes)}")
        for idx in indexes:
            print(f"   - {idx[1]}.{idx[0]}")

        print("\n" + "=" * 80)
        print("VERIFICAÇÃO CONCLUÍDA")
        print("=" * 80)


if __name__ == "__main__":
    verify_migration()
