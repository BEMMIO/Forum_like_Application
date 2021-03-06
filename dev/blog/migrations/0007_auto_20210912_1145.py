# Generated by Django 3.2.7 on 2021-09-12 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_article_content'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-created_date',), 'verbose_name': 'Article', 'verbose_name_plural': "Article's"},
        ),
        migrations.AddField(
            model_name='board',
            name='joined_users_count',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='joined users'),
        ),
        migrations.AddField(
            model_name='board',
            name='last_article_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='board',
            name='last_article_posted_by',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='last article posted by'),
        ),
        migrations.AddField(
            model_name='board',
            name='last_article_title',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='board color'),
        ),
    ]
