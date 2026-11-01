import os
import runpy

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = '数据初始化：清空业务/账号数据并按 seed.py 重建初始演示数据'

    def handle(self, *args, **options):
        backend_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        seed_path = os.path.join(backend_dir, 'seed.py')
        if not os.path.exists(seed_path):
            raise CommandError(f'未找到 seed.py（{seed_path}），无法初始化')
        self.stdout.write('开始数据初始化（seed.py 重建中，请稍候）…')
        runpy.run_path(seed_path, run_name='__main__')
        self.stdout.write(self.style.SUCCESS('数据初始化完成'))
