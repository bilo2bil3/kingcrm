# Generated by Django 3.1.4 on 2022-05-09 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0017_auto_20220505_2354'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='service',
            field=models.CharField(default='', max_length=64),
        ),
    ]