# Generated by Django 3.2.5 on 2021-12-20 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_rename_description_article_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tags',
            name='active',
        ),
        migrations.RemoveField(
            model_name='tags',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='tags',
            name='image',
        ),
        migrations.RemoveField(
            model_name='tags',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='tags',
            name='updated_date',
        ),
    ]