# Generated by Django 4.2.3 on 2024-10-09 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_plans_plan_alter_plans_plan_name_alter_plans_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkoutTutorial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('link', models.URLField()),
            ],
        ),
    ]
