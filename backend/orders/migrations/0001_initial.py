
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('product', '作品'), ('course', '课程')], default='product', max_length=20, verbose_name='订单类型')),
                ('item_name', models.CharField(max_length=200, verbose_name='商品名称')),
                ('glyph', models.CharField(blank=True, default='盏', max_length=10, verbose_name='图标字')),
                ('buyer', models.CharField(blank=True, max_length=50, verbose_name='买家昵称')),
                ('buyer_phone', models.CharField(blank=True, max_length=20, verbose_name='买家电话')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='实付金额')),
                ('status', models.CharField(choices=[('pending', '待付款'), ('paid', '已付款·待发货'), ('shipped', '已发货'), ('done', '已完成')], default='pending', max_length=20, verbose_name='状态')),
                ('pay_method', models.CharField(blank=True, max_length=20, verbose_name='支付方式')),
                ('order_time', models.CharField(blank=True, max_length=30, verbose_name='下单时间')),
                ('pay_time', models.CharField(blank=True, max_length=30, verbose_name='支付时间')),
                ('receiver', models.CharField(blank=True, max_length=50, verbose_name='收件人')),
                ('address', models.CharField(blank=True, max_length=200, verbose_name='收货地址')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='收货电话')),
                ('remark', models.TextField(blank=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('buyer_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='my_orders', to=settings.AUTH_USER_MODEL, verbose_name='买家账号')),
                ('seller', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sold_orders', to='accounts.inheritor', verbose_name='卖家(传承人)')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'db_table': 'orders_order',
                'ordering': ['-id'],
            },
        ),
    ]
