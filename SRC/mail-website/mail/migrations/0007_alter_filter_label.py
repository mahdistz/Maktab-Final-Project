# Generated by Django 3.2 on 2022-03-23 12:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0006_auto_20220323_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filter',
            name='label',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='label', to='mail.category'),
        ),
    ]
