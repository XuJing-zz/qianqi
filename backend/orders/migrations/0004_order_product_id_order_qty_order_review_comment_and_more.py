
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product_id',
            field=models.PositiveIntegerField(default=0, verbose_name='关联作品ID'),
        ),
        migrations.AddField(
            model_name='order',
            name='qty',
            field=models.PositiveIntegerField(default=1, verbose_name='购买数量'),
        ),
        migrations.AddField(
            model_name='order',
            name='review_comment',
            field=models.TextField(blank=True, verbose_name='审核意见/驳回原因'),
        ),
        migrations.AddField(
            model_name='order',
            name='source',
            field=models.CharField(blank=True, default='auto', max_length=20, verbose_name='订单来源'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('review', '待审核'), ('pending', '待付款'), ('paid', '待发货'), ('shipped', '已发货'), ('done', '已完成'), ('cancelled', '已取消'), ('rejected', '已驳回')], default='pending', max_length=20, verbose_name='状态'),
        ),
    ]
