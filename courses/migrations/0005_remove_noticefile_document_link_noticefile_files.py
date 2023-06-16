# Generated by Django 4.1.5 on 2023-02-25 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_merge_20220713_1224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='noticefile',
            name='document_link',
        ),
        migrations.AddField(
            model_name='noticefile',
            name='files',
            field=models.FileField(default=1, upload_to='subs/files/'),
            preserve_default=False,
        ),
    ]
