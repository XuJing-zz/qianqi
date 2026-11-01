
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='company',
            field=models.CharField(blank=True, max_length=50, verbose_name='物流公司'),
        ),
        migrations.AddField(
            model_name='order',
            name='ship_time',
            field=models.CharField(blank=True, max_length=30, verbose_name='发货时间'),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_no',
            field=models.CharField(blank=True, max_length=100, verbose_name='物流单号'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', '待付款'), ('paid', '已付款·待发货'), ('shipped', '已发货'), ('done', '已完成'), ('cancelled', '已取消')], default='pending', max_length=20, verbose_name='状态'),
        ),
    ]
