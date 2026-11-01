
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0007_skill_cautions_skill_hard_points_skill_raw_materials_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='school',
            field=models.CharField(blank=True, max_length=50, verbose_name='工艺流派'),
        ),
    ]
