
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_student_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='review_comment',
            field=models.TextField(blank=True, verbose_name='报名审核意见'),
        ),
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.CharField(choices=[('review', '待审核'), ('rejected', '已驳回'), ('ongoing', '进行中'), ('done', '已完成')], default='ongoing', max_length=20, verbose_name='状态'),
        ),
    ]
