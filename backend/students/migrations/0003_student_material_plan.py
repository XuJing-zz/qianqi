
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_trainingrecord_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='material_plan',
            field=models.JSONField(blank=True, default=list, verbose_name='材料包配置'),
        ),
    ]
