
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_feedbackmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackmessage',
            name='contact',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='联系方式'),
        ),
    ]
