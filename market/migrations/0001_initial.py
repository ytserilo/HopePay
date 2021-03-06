# Generated by Django 2.1.7 on 2019-08-05 11:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('UserProfile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='product_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Заголовок', max_length=255)),
                ('location', models.CharField(default='Місце', max_length=512)),
                ('description', models.TextField()),
                ('amount', models.IntegerField(verbose_name='Сума')),
                ('currency', models.CharField(max_length=5, verbose_name='Валюта')),
                ('payment_desciption', models.TextField()),
                ('installments_count', models.IntegerField(blank=True, null=True)),
                ('count_of_paid_parts', models.IntegerField(blank=True, null=True)),
                ('postal_transfer', models.BooleanField(blank=True)),
                ('active_status', models.BooleanField(default=True)),
                ('seller', models.BooleanField()),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author_product', to='UserProfile.CustomUser')),
            ],
        ),
        migrations.AddField(
            model_name='images',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='market.Product'),
        ),
    ]
