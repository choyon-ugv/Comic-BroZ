# Generated by Django 5.2 on 2025-05-06 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_charactercard_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='comic',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
