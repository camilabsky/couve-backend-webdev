from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=64)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
            ],
            options={
                'db_table': 'Perfil',
            },
        ),
        migrations.CreateModel(
            name='Recompensas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=128)),
                ('descricao', models.TextField()),
                ('preco', models.IntegerField()),
                ('tipo', models.CharField(max_length=32)),
                ('src', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'Recompensas',
            },
        ),
        migrations.CreateModel(
            name='Tarefas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=128)),
                ('tipo', models.CharField(max_length=32)),
                ('dificuldade', models.IntegerField()),
                ('horta', models.CharField(max_length=128)),
                ('descricao', models.CharField(max_length=128)),
                ('concluido', models.BooleanField(default=False)),
                ('moedas', models.IntegerField()),
                ('mudas', models.IntegerField()),
                ('tempo', models.IntegerField()),
                ('id_perfil', models.ForeignKey(
                    blank=True,
                    db_column='id_perfil',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='app.perfil',
                )),
            ],
            options={
                'db_table': 'Tarefas',
            },
        ),
        migrations.CreateModel(
            name='PerfilRecompensas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_perfil', models.ForeignKey(
                    blank=True,
                    db_column='id_perfil',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='app.perfil',
                )),
                ('id_recompensa', models.ForeignKey(
                    db_column='id_recompensa',
                    on_delete=django.db.models.deletion.CASCADE,
                    to='app.recompensas',
                )),
            ],
            options={
                'db_table': 'PerfilRecompensas',
            },
        ),
    ]
