# Generated by Django 4.2.5 on 2023-09-10 22:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
