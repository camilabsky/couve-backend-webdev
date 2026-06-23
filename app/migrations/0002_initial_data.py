from django.db import migrations


def load_initial_data(apps, schema_editor):
    Perfil = apps.get_model('app', 'Perfil')
    Recompensas = apps.get_model('app', 'Recompensas')
    Tarefas = apps.get_model('app', 'Tarefas')
    PerfilRecompensas = apps.get_model('app', 'PerfilRecompensas')

    # Insert Perfil
    perfis_data = [
        {"nome": "Maria Silva", "email": "maria.silva@horta.com"},
        {"nome": "João Pereira", "email": "joao.pereira@horta.com"},
        {"nome": "Ana Souza", "email": "ana.souza@horta.com"},
    ]
    perfis = []
    for perfil_data in perfis_data:
        perfis.append(Perfil.objects.create(**perfil_data))

    # Insert Tarefas
    tarefas_data = [
        {
            "titulo": "Preparar composto orgânico",
            "tipo": "compostagem",
            "horta": "Horta Comunitária Centro",
            "descricao": "Preparar composto orgânico",
            "dificuldade": 2,
            "moedas": 150,
            "mudas": 0,
            "tempo": 60,
        },
        {
            "titulo": "Regar plantas da seção A",
            "tipo": "Manutenção",
            "horta": "Horta Comunitária Centro",
            "descricao": "Realizar a rega das plantas na seção A do jardim durante a manhã",
            "dificuldade": 0,
            "moedas": 50,
            "mudas": 0,
            "tempo": 30,
        },
        {
            "titulo": "Capinar canteiro de tomates",
            "tipo": "Manutenção",
            "horta": "Jardim da Praça Verde",
            "descricao": "Remover ervas daninhas do canteiro de tomates",
            "dificuldade": 1,
            "moedas": 80,
            "mudas": 0,
            "tempo": 60,
        },
        {
            "titulo": "Plantar mudas de alface",
            "tipo": "Plantio",
            "horta": "Horta Comunitária Centro",
            "descricao": "Plantar 20 mudas de alface na área designada",
            "dificuldade": 1,
            "moedas": 120,
            "mudas": 20,
            "tempo": 90,
        },
        {
            "titulo": "Colher vegetais maduros",
            "tipo": "colheita",
            "horta": "Horta Orgânica Vila Nova",
            "descricao": "Fazer a colheita dos vegetais que estão prontos",
            "dificuldade": 0,
            "moedas": 100,
            "mudas": 0,
            "tempo": 45,
        },
    ]
    for t in tarefas_data:
        Tarefas.objects.create(**t)

    # Insert Recompensas
    recompensas_data = [
        {"nome": "Cesta de Vegetais Orgânicos", "descricao": "Cesta com vegetais frescos da horta", "tipo": "Produtos", "preco": 200, "src": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400"},
        {"nome": "Kit de Ferramentas de Jardim", "descricao": "Kit básico com pá, rastelo e luvas", "tipo": "Ferramentas", "preco": 500, "src": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400"},
        {"nome": "Mudas de Ervas Aromáticas", "descricao": "5 mudas de manjericão, tomilho e alecrim", "tipo": "Plantas", "preco": 150, "src": "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=400"},
        {"nome": "Workshop de Compostagem", "descricao": "Acesso ao workshop sobre compostagem doméstica", "tipo": "Educação", "preco": 300, "src": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400"},
        {"nome": "Sacola Ecológica Personalizada", "descricao": "Sacola reutilizável com logo da horta", "tipo": "Acessórios", "preco": 100, "src": "https://images.unsplash.com/photo-1553531087-1ea13dd840ad?w=400"},
        {"nome": "Cesta Premium de Vegetais", "descricao": "Cesta especial com vegetais selecionados", "tipo": "Produtos", "preco": 800, "src": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400"},
    ]
    for r in recompensas_data:
        Recompensas.objects.create(**r)

    # Insert PerfilRecompensas (id_perfil left NULL)
    rec_ids = list(Recompensas.objects.values_list('id', flat=True))
    counts = [5, 2, 8, 10, 15, 3]
    for rec_id, cnt in zip(rec_ids, counts):
        for _ in range(cnt):
            PerfilRecompensas.objects.create(id_recompensa_id=rec_id)


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_initial_data, migrations.RunPython.noop),
    ]
