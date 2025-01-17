# Generated by Django 3.2.7 on 2021-09-12 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order_app', '0002_orderitem_product_info'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user_app.contact', verbose_name='Контакт'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='orderitem',
            constraint=models.UniqueConstraint(fields=('order_id', 'product_info'), name='unique_order_item'),
        ),
    ]
