# Generated by Django 3.0.5 on 2020-04-29 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='archivo',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='item',
            name='char',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
