# Generated by Django 3.2.7 on 2021-10-05 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20211004_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_hashed',
            field=models.CharField(blank=True, max_length=355, null=True, verbose_name='e-mail hashed'),
        ),
    ]
