
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='alert_threshold',
            field=models.PositiveIntegerField(default=5, verbose_name='库存预警值'),
        ),
        migrations.AddField(
            model_name='product',
            name='cost_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='成本价'),
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0, verbose_name='当前库存'),
        ),
        migrations.CreateModel(
            name='ProductStockRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(blank=True, max_length=200, verbose_name='作品名')),
                ('type', models.CharField(choices=[('in', '入库'), ('out', '出库'), ('order', '销售出库'), ('loss', '损耗')], default='in', max_length=20, verbose_name='类型')),
                ('qty', models.PositiveIntegerField(default=0, verbose_name='数量')),
                ('note', models.CharField(blank=True, max_length=200, verbose_name='备注')),
                ('operator', models.CharField(blank=True, max_length=50, verbose_name='操作人')),
                ('time', models.CharField(blank=True, max_length=30, verbose_name='时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_records', to='products.product', verbose_name='作品')),
            ],
            options={
                'verbose_name': '作品出入库流水',
                'verbose_name_plural': '作品出入库流水',
                'db_table': 'products_stockrecord',
                'ordering': ['-id'],
            },
        ),
    ]
