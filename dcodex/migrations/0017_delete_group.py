# Generated by Django 2.2.2 on 2020-05-27 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcodex', '0016_delete_groupmembershipbase'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Group',
        ),
    ]