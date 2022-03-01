# Generated by Django 3.2 on 2022-03-01 18:48

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_auto_20220225_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coderegister',
            name='phone_number',
            field=models.CharField(max_length=11, validators=[user.models.MobileNumberValidator()]),
        ),
        migrations.AlterField(
            model_name='users',
            name='phone',
            field=models.CharField(error_messages={'unique': 'A user with that Phone number already exists.'}, help_text='Example : 09125573688', max_length=11, unique=True, validators=[user.models.MobileNumberValidator()], verbose_name='Phone Number'),
        ),
    ]
