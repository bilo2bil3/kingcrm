# Generated by Django 4.0.5 on 2022-06-16 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0027_alter_lead_age_alter_lead_campaign_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='organisation',
        ),
        migrations.AddField(
            model_name='category',
            name='organisation',
            field=models.ManyToManyField(to='leads.userprofile'),
        ),
    ]