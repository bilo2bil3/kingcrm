# Generated by Django 3.1.4 on 2022-07-07 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0026_auto_20220622_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='Q1',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='Q2',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='Q3',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='Q4',
            field=models.TextField(blank=True),
        ),
    ]