# Generated by Django 4.2.1 on 2023-05-12 03:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_post_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='user',
            new_name='author',
        ),
    ]
