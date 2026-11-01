
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_student_material_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='completed',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='已学课时标识'),
        ),
    ]
