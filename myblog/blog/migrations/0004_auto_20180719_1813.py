# Generated by Django 2.0.1 on 2018-07-19 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20180719_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='article_id',
            field=models.CharField(default='6169941.html', max_length=32),
        ),
    ]
