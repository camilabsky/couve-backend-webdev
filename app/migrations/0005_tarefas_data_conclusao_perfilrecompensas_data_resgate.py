from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_perfil_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilrecompensas',
            name='data_resgate',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tarefas',
            name='data_conclusao',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
