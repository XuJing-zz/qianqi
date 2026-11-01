
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='物料名')),
                ('spec', models.CharField(blank=True, max_length=100, verbose_name='规格说明')),
                ('type', models.CharField(choices=[('material', '基础材料'), ('tool', '工具')], default='material', max_length=20, verbose_name='类型')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='当前库存')),
                ('alert_threshold', models.PositiveIntegerField(default=0, verbose_name='告警阈值')),
                ('linked_course_id', models.PositiveIntegerField(default=0, verbose_name='关联课程ID')),
                ('linked_course_name', models.CharField(blank=True, max_length=200, verbose_name='关联课程名')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '物料',
                'verbose_name_plural': '物料',
                'db_table': 'inventory_material',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.PositiveIntegerField(default=0, verbose_name='学员ID')),
                ('student_name', models.CharField(blank=True, max_length=50, verbose_name='学员名')),
                ('course_id', models.PositiveIntegerField(default=0, verbose_name='课程ID')),
                ('course_name', models.CharField(blank=True, max_length=200, verbose_name='课程名')),
                ('items', models.JSONField(blank=True, default=list, verbose_name='物料清单')),
                ('status', models.CharField(choices=[('pending', '待寄'), ('shipped', '已寄'), ('signed', '已签收')], default='pending', max_length=20, verbose_name='状态')),
                ('company', models.CharField(blank=True, max_length=50, verbose_name='快递公司')),
                ('tracking_no', models.CharField(blank=True, max_length=100, verbose_name='快递单号')),
                ('ship_time', models.CharField(blank=True, max_length=30, verbose_name='发货时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '邮寄记录',
                'verbose_name_plural': '邮寄记录',
                'db_table': 'inventory_shipment',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='StockRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_name', models.CharField(blank=True, max_length=100, verbose_name='物料名')),
                ('type', models.CharField(choices=[('in', '入库'), ('out', '领用出库'), ('loss', '损耗')], default='in', max_length=20, verbose_name='类型')),
                ('qty', models.PositiveIntegerField(default=0, verbose_name='数量')),
                ('note', models.CharField(blank=True, max_length=200, verbose_name='备注')),
                ('operator', models.CharField(blank=True, max_length=50, verbose_name='操作人')),
                ('time', models.CharField(blank=True, max_length=30, verbose_name='时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_records', to='inventory.material', verbose_name='物料')),
            ],
            options={
                'verbose_name': '出入库流水',
                'verbose_name_plural': '出入库流水',
                'db_table': 'inventory_stockrecord',
                'ordering': ['-id'],
            },
        ),
    ]
