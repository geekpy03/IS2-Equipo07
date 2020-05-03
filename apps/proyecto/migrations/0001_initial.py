# Generated by Django 3.0.5 on 2020-05-03 17:47

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.TextField()),
                ('fecha_creacion', models.DateField(default=datetime.date.today)),
                ('ultima_modificacion', models.DateTimeField(auto_now=True)),
                ('estado', models.CharField(choices=[('Pendiente', 'Pendiente'), ('Iniciado', 'Iniciado'), ('Cancelado', 'Cancelado'), ('Finalizado', 'Finalizado')], default='Pendiente', max_length=30)),
                ('slug', models.CharField(default='', max_length=50)),
                ('miembros', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gerente', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('Can add proyecto', 'Puede crear un proyecto'), ('Can change proyecto', 'Puede editar el proyecto'), ('Can delete proyecto', 'Puede eliminar un proyecto'), ('Can view proyecto', 'Puede visualizar un proyecto')],
            },
        ),
    ]
