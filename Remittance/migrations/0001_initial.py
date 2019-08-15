# Generated by Django 2.1.7 on 2019-08-05 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChangesAwaitingConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('amount', models.IntegerField()),
                ('currency', models.CharField(max_length=5, verbose_name='Валюта')),
                ('postal_transfer', models.BooleanField(blank=True, null=True)),
                ('payment_by_installments', models.BooleanField(blank=True, null=True)),
                ('installments_count', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Remittance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_link', models.CharField(max_length=32)),
                ('postal_code', models.CharField(blank=True, max_length=255, verbose_name='Номер накладної')),
                ('postal_transfer', models.BooleanField(blank=True)),
                ('paid', models.BooleanField(default=False)),
                ('shipped', models.BooleanField(default=False)),
                ('postal_phone', models.CharField(blank=True, max_length=12)),
                ('successful', models.BooleanField(blank=True, null=True)),
                ('date_payed', models.CharField(blank=True, max_length=255)),
                ('amount', models.IntegerField(verbose_name='Сума')),
                ('currency', models.CharField(max_length=5, verbose_name='Валюта')),
                ('payment_desciption', models.TextField()),
                ('payment_by_installments', models.BooleanField(blank=True, null=True)),
                ('installments_count', models.IntegerField(blank=True, null=True)),
                ('count_of_paid_parts', models.IntegerField(blank=True, null=True)),
                ('liqpay_order_id', models.CharField(blank=True, max_length=512)),
            ],
        ),
    ]
