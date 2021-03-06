# Generated by Django 3.2.7 on 2021-09-11 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210911_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_moderator',
            field=models.BooleanField(blank=True, default=False, help_text='Designates whether the user has moderators privileges.', null=True),
        ),
    ]
