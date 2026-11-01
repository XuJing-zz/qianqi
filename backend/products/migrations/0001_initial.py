
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
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('glyph', models.CharField(blank=True, default='作', max_length=10, verbose_name='图标字')),
                ('name', models.CharField(max_length=200, verbose_name='作品名称')),
                ('craft', models.CharField(blank=True, max_length=50, verbose_name='技艺')),
                ('category', models.CharField(blank=True, max_length=50, verbose_name='分类')),
                ('material', models.CharField(blank=True, max_length=200, verbose_name='材质')),
                ('size', models.CharField(blank=True, max_length=200, verbose_name='尺寸')),
                ('inheritor', models.CharField(blank=True, max_length=100, verbose_name='作者/传承人')),
                ('level', models.CharField(blank=True, max_length=20, verbose_name='传承等级')),
                ('saleable', models.BooleanField(default=True, verbose_name='是否可售')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='售价')),
                ('cover', models.CharField(blank=True, max_length=300, verbose_name='封面图')),
                ('images', models.JSONField(blank=True, default=list, verbose_name='照片集')),
                ('story', models.TextField(blank=True, verbose_name='作品故事')),
                ('highlights', models.JSONField(blank=True, default=list, verbose_name='作品亮点')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('pending', '待审核'), ('approved', '已通过'), ('rejected', '已驳回'), ('offline', '已下架')], default='draft', max_length=20, verbose_name='状态')),
                ('flag', models.CharField(blank=True, max_length=20, verbose_name='角标')),
                ('submit_time', models.CharField(blank=True, max_length=30, verbose_name='提交时间')),
                ('review_comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='accounts.inheritor', verbose_name='所属传承人')),
            ],
            options={
                'verbose_name': '文创作品',
                'verbose_name_plural': '文创作品',
                'db_table': 'products_product',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='收藏用户')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='products.product', verbose_name='收藏作品')),
            ],
            options={
                'verbose_name': '收藏',
                'verbose_name_plural': '收藏',
                'db_table': 'products_favorite',
                'ordering': ['-id'],
                'unique_together': {('user', 'product')},
            },
        ),
    ]
