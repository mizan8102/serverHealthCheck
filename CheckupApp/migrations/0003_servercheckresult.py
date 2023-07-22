# Generated by Django 4.2.3 on 2023-07-22 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CheckupApp', '0002_alter_serverinfo_ip_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerCheckResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_time', models.CharField(max_length=200)),
                ('status_code', models.IntegerField(max_length=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('server_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CheckupApp.serverinfo')),
            ],
        ),
    ]