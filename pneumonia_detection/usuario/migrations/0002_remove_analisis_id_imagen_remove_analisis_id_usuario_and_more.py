# Generated by Django 5.1.1 on 2024-09-19 19:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analisis',
            name='id_imagen',
        ),
        migrations.RemoveField(
            model_name='analisis',
            name='id_usuario',
        ),
        migrations.RemoveField(
            model_name='imagenes',
            name='id_historia',
        ),
        migrations.RemoveField(
            model_name='imagenes',
            name='id_usuario',
        ),
        migrations.AddField(
            model_name='analisis',
            name='id_Hpaciente',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usuario.historiapaciente'),
        ),
        migrations.AddField(
            model_name='historiapaciente',
            name='id_usuario',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usuario.usuario'),
        ),
        migrations.AddField(
            model_name='imagenes',
            name='id_analisis',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usuario.analisis'),
        ),
        migrations.AlterField(
            model_name='historiapaciente',
            name='observaciones',
            field=models.TextField(),
        ),
    ]