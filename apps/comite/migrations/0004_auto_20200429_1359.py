# Generated by Django 3.0.5 on 2020-04-29 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0007_auto_20200426_1819'),
        ('comite', '0003_auto_20200426_0055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comite',
            name='proyecto',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.Proyecto'),
        ),
    ]
