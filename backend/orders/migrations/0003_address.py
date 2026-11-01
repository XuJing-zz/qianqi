
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_company_order_ship_time_order_tracking_no_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.CharField(max_length=50, verbose_name='收货人')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='联系电话')),
                ('province', models.CharField(blank=True, max_length=50, verbose_name='省')),
                ('city', models.CharField(blank=True, max_length=50, verbose_name='市')),
                ('district', models.CharField(blank=True, max_length=50, verbose_name='区/县')),
                ('detail', models.CharField(blank=True, max_length=200, verbose_name='详细地址')),
                ('is_default', models.BooleanField(default=False, verbose_name='是否默认')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='所属用户')),
            ],
            options={
                'verbose_name': '收货地址',
                'verbose_name_plural': '收货地址',
                'db_table': 'orders_address',
                'ordering': ['-is_default', '-id'],
            },
        ),
    ]
