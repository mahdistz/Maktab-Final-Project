# Generated by Django 3.2 on 2022-02-23 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20220223_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='verification',
            field=models.CharField(choices=[('Phone', 'Phone_number'), ('Email', 'Email')], default='', max_length=100),
        ),
    ]
