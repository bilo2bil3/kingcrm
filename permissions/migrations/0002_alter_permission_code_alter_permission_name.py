# Generated by Django 4.0.5 on 2022-06-08 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='code',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='permission',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]