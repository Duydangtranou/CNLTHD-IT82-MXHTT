# Generated by Django 3.2.5 on 2021-12-25 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_action_articleview_comment_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.user'),
            preserve_default=False,
        ),
    ]