# Generated by Django 3.0.11 on 2020-11-26 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcodex', '0031_auto_20201124_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verselocation',
            name='page',
            field=models.IntegerField(blank=True, default=None, help_text='DEPRECATED', null=True),
        ),
        migrations.AlterField(
            model_name='verselocation',
            name='pdf',
            field=models.ForeignKey(blank=True, default=None, help_text='DEPRECATED', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='dcodex.PDF'),
        ),
    ]