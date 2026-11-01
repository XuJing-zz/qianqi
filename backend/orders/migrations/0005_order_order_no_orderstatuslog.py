
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_product_id_order_qty_order_review_comment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_no',
            field=models.CharField(blank=True, db_index=True, default='', max_length=50, verbose_name='订单编号'),
        ),
        migrations.CreateModel(
            name='OrderStatusLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_status', models.CharField(blank=True, default='', max_length=20, verbose_name='原状态')),
                ('to_status', models.CharField(blank=True, default='', max_length=20, verbose_name='新状态')),
                ('operator', models.CharField(blank=True, default='', max_length=50, verbose_name='操作人')),
                ('note', models.CharField(blank=True, default='', max_length=200, verbose_name='说明')),
                ('time', models.CharField(blank=True, default='', max_length=30, verbose_name='操作时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_logs', to='orders.order', verbose_name='订单')),
            ],
            options={
                'verbose_name': '订单状态变更',
                'verbose_name_plural': '订单状态变更',
                'db_table': 'orders_status_log',
                'ordering': ['id'],
            },
        ),
    ]
