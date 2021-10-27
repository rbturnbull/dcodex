# Generated by Django 2.2.2 on 2020-05-26 05:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("dcodex", "0004_auto_20190927_0054"),
    ]

    operations = [
        migrations.AlterField(
            model_name="manuscript",
            name="name",
            field=models.CharField(
                blank=True,
                help_text="A descriptive string for this manuscript.",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="manuscript",
            name="siglum",
            field=models.CharField(
                blank=True,
                help_text="A unique short string for this manuscript.",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="verse",
            name="rank",
            field=models.IntegerField(
                help_text="An integer to enable sorting of the verses (deprecated)"
            ),
        ),
        migrations.AlterField(
            model_name="verselocation",
            name="x",
            field=models.FloatField(
                help_text="The number of horizontal pixels from the left of the facsimile image to the the location of the verse, normalized by the height of the image."
            ),
        ),
        migrations.AlterField(
            model_name="verselocation",
            name="y",
            field=models.FloatField(
                help_text="The number of vertical pixels from the top of the facsimile image to the the location of the verse, normalized by the height of the image."
            ),
        ),
        migrations.AlterField(
            model_name="versetranscriptionbase",
            name="manuscript",
            field=models.ForeignKey(
                help_text="The manuscript this transcription is from.",
                on_delete=django.db.models.deletion.CASCADE,
                to="dcodex.Manuscript",
            ),
        ),
        migrations.AlterField(
            model_name="versetranscriptionbase",
            name="transcription",
            field=models.CharField(
                help_text="The unnormalized text of this transcription.",
                max_length=1024,
            ),
        ),
        migrations.AlterField(
            model_name="versetranscriptionbase",
            name="verse",
            field=models.ForeignKey(
                help_text="The verse of this transcription.",
                on_delete=django.db.models.deletion.CASCADE,
                to="dcodex.Verse",
            ),
        ),
    ]
