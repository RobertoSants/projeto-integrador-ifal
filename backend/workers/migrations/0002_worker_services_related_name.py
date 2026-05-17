from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0001_initial"),
        ("workers", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="worker",
            name="services",
            field=models.ManyToManyField(
                blank=True,
                related_name="workers",
                to="services.servicecategory",
            ),
        ),
    ]
