# Generated by Django 3.2.7 on 2021-10-05 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0005_alter_invitation_invite_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitation',
            name='sent_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Sent Date'),
        ),
    ]
