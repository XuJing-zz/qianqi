
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='heritageprofile',
            name='cert_files',
            field=models.JSONField(blank=True, default=list, verbose_name='荣誉证书附件'),
        ),
    ]
