# Generated by Django 2.0 on 2018-09-20 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DNSmisconfiguration', '0003_auto_20180920_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='RootDNSServers',
            fields=[
                ('host_name', models.CharField(default='', max_length=256, primary_key=True, serialize=False)),
                ('ipv4_address', models.GenericIPAddressField(protocol='IPv4')),
                ('ipv6_address', models.GenericIPAddressField(protocol='IPv6')),
                ('description', models.CharField(default='', max_length=512)),
            ],
        ),
    ]
