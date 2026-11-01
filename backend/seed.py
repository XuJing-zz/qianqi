import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Admin, Inheritor
from heritage.models import HeritageProfile
from orders.models import Order, Address
from students.models import Student, TrainingRecord
from skills.models import Skill
from products.models import Product, ProductStockRecord, Favorite
from courses.models import Course
from inventory.models import Material, StockRecord, Shipment
from system.models import OperationLog, SystemConfig, FeedbackMessage
from datetime import date, timedelta

ADMIN_PWD = '123456'

SAMPLE_VIDEO = 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4'

ONLINE_VENUES = [
    '线上授课 · 腾讯会议',
    '线上授课 · 钉钉',
    '线上授课 · 飞书',
    '线上授课 · 微信视频号',
    '线上授课 · 抖音直播',
    '线上授课 · 平台直播间',
]

ACCOUNTS = [
    dict(username='admin', role='admin', name='平台管理员', nick='千漆运营',
         gender='男', region='四川省成都市', bio='漆器非遗平台运营方，负责内容审核与进销存管理。',
         phone='138****0001', email='admin@qianqi.cn',
         level='', craft='', years=None, intro='让千年漆艺走进生活', honor='', status='active'),
    dict(username='heritage01', role='heritage', name='张守一', nick='髹漆老人',
         gender='男', region='四川省成都市', bio='髹漆四十余年，师承川派漆艺，门下弟子遍及南北，常年在成都开设髹漆工作坊。',
         phone='138****8888', email='zhang@qianqi.cn',
         level='国家级', craft='髹漆', years=40, intro='髹漆为骨，镏金点睛', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage02', role='heritage', name='赵雕', nick='北派雕漆',
         gender='男', region='北京市东城区', bio='师承北派雕漆传人，擅长剔犀云纹与剔红，刀法利落。',
         phone='138****8889', email='zhao@qianqi.cn',
         level='国家级', craft='雕漆', years=22, intro='以刀代笔，刀下有乾坤', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage03', role='heritage', name='姚镜春', nick='京华金漆',
         gender='女', region='北京市东城区', bio='传承京作金漆镶嵌髹饰技艺，主攻百宝嵌与玉石镶嵌漆器。',
         phone='138****8892', email='yao@qianqi.cn',
         level='国家级', craft='金漆镶嵌', years=30, intro='宝色流光，嵌里藏金', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage04', role='heritage', name='郑寿山', nick='平遥推光人',
         gender='男', region='山西省晋中市平遥县', bio='以平遥推光漆器为业，手掌推光一脉相承，坚守「髹漆—推光」古法。',
         phone='138****8893', email='zheng@qianqi.cn',
         level='国家级', craft='推光漆', years=36, intro='一掌推光，镜里见心', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage05', role='heritage', name='卫子谦', nick='绛州云雕',
         gender='男', region='山西省运城市新绛县', bio='绛州剔犀世家出身，专攻云纹剔犀（云雕），刀口层色分明。',
         phone='138****8894', email='wei@qianqi.cn',
         level='国家级', craft='剔犀', years=34, intro='一剔见三层色', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage06', role='heritage', name='李爱华', nick='稷山贝华',
         gender='女', region='山西省运城市稷山县', bio='以软螺钿镶嵌漆器见长，贝片薄如蝉翼，嵌花温润流光。',
         phone='138****8895', email='li@qianqi.cn',
         level='国家级', craft='螺钿', years=40, intro='贝华入漆，流光千年', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage07', role='heritage', name='沈砚秋', nick='广陵漆人',
         gender='女', region='江苏省扬州市', bio='扬州漆器髹饰技艺传人，兼习点螺、平磨螺钿与雕漆嵌玉诸法。',
         phone='138****8896', email='shen@qianqi.cn',
         level='国家级', craft='扬州漆器', years=32, intro='千里漆器出广陵', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage08', role='heritage', name='温知远', nick='吴门款彩',
         gender='男', region='江苏省苏州市姑苏区', bio='专研苏州漆器款彩（刻灰填彩）与素髹揩漆，屏风挂屏一绝。',
         phone='138****8897', email='wen@qianqi.cn',
         level='省级', craft='款彩', years=33, intro='刻灰填彩，山水可触', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage09', role='heritage', name='梁福宁', nick='闽都脱胎',
         gender='女', region='福建省福州市', bio='福州脱胎漆器髹饰技艺传人，脱胎成器、轻巧坚固，长于闪光髹饰。',
         phone='138****8898', email='liang@qianqi.cn',
         level='国家级', craft='脱胎漆器', years=46, intro='脱胎换骨，如羽之轻', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage10', role='heritage', name='蔡水镜', nick='鹭岛漆线',
         gender='男', region='福建省厦门市', bio='厦门漆线雕技艺传人，捻线盘绕、贴金庄严，专攻神佛造像装饰。',
         phone='138****8899', email='cai@qianqi.cn',
         level='国家级', craft='漆线雕', years=44, intro='一线盘千年', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage11', role='heritage', name='林正源', nick='泉州漆彩',
         gender='男', region='福建省泉州市', bio='承泉州漆线雕与永春漆篮两艺，竹篮髹漆、堆雕彩绘皆通。',
         phone='138****8900', email='lin@qianqi.cn',
         level='省级', craft='漆线雕', years=28, intro='篮中盛海味，漆里见匠心', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage12', role='heritage', name='童启山', nick='天台漆佛',
         gender='男', region='浙江省台州市', bio='天台山干漆夹苎技艺传人，以漆麻裱塑佛像，也擅临海犀皮漆艺。',
         phone='138****8901', email='tong@qianqi.cn',
         level='国家级', craft='夹苎脱胎', years=52, intro='干漆夹苎，庄严不朽', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage13', role='heritage', name='何元章', nick='甬上漆金',
         gender='男', region='浙江省宁波市', bio='传宁波泥金彩漆与朱金漆木雕，漆金并重，曾为十里红妆髹嫁奁。',
         phone='138****8902', email='he@qianqi.cn',
         level='国家级', craft='泥金彩漆', years=41, intro='朱漆为地，真金作华', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage14', role='heritage', name='吴乐清', nick='瓯江漆髹',
         gender='女', region='浙江省温州市平阳县', bio='平阳漆器制作技艺传人，髹涂推光、日用陈设皆善，一脉承宋元温州漆器之遗风。',
         phone='138****8903', email='wu@qianqi.cn',
         level='省级', craft='平阳漆器', years=39, intro='髹里见宋韵，漆中有匠心', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage15', role='heritage', name='甘玉成', nick='徽州犀皮',
         gender='男', region='安徽省黄山市屯溪区', bio='徽州漆器髹饰技艺传人，擅犀皮（菠萝漆）与漆砂砚，恢复古法打埝起纹。',
         phone='138****8904', email='gan@qianqi.cn',
         level='国家级', craft='犀皮漆', years=37, intro='斑斓天然，犀皮第一', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage16', role='heritage', name='邹槐安', nick='荆楚漆髹',
         gender='男', region='湖北省荆州市', bio='楚式漆器髹饰技艺传人，髹漆彩绘楚风纹样，兼事出土漆木器修复。',
         phone='138****8905', email='zou@qianqi.cn',
         level='国家级', craft='髹漆彩绘', years=43, intro='朱黑之间，凤鸣千年', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage17', role='heritage', name='陈其梁', nick='坝漆之子',
         gender='男', region='湖北省恩施州利川市', bio='利川坝漆割漆制漆传人，「坝漆名冠全球」之乡的生漆匠。',
         phone='138****8906', email='chen@qianqi.cn',
         level='国家级', craft='制漆', years=41, intro='割得一树漆，养得一城器', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage18', role='heritage', name='龙漫', nick='渝派研磨彩绘',
         gender='女', region='重庆市渝中区', bio='重庆漆器髹饰技艺传人，长于研磨彩绘与堆漆研磨，漆面沉静多变。',
         phone='138****8907', email='long@qianqi.cn',
         level='国家级', craft='研磨彩绘', years=38, intro='磨出来的彩，养出来的光', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage19', role='heritage', name='吉伍阿依', nick='凉山彝漆',
         gender='女', region='四川省凉山州喜德县', bio='彝族漆器髹饰技艺传人，黑红黄三色手绘，纹样取自日月山川。',
         phone='138****8908', email='jiwu@qianqi.cn',
         level='国家级', craft='彝族漆器', years=46, intro='一器三色，彝家天工', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage20', role='heritage', name='高小梅', nick='大方漆艺',
         gender='女', region='贵州省毕节市大方县', bio='贵州大方彝族漆器传人，皮木胎髹漆彩绘，漆器经久耐用。',
         phone='138****8909', email='gao@qianqi.cn',
         level='国家级', craft='彝族漆器', years=44, intro='大方漆器，千年不腐', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage21', role='heritage', name='周子萍', nick='鄱湖脱胎',
         gender='女', region='江西省上饶市鄱阳县', bio='鄱阳脱胎漆器髹饰技艺传人，脱胎胎薄如纸、坚如瓷，兼研婺源菠萝漆。',
         phone='138****8910', email='zhou@qianqi.cn',
         level='国家级', craft='脱胎漆器', years=35, intro='鄱湖一叶，脱胎生辉', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage22', role='heritage', name='张铁山', nick='天水雕填',
         gender='男', region='甘肃省天水市秦州区', bio='天水雕漆传人，以雕填、石刻镶嵌与彩绘见长，擅作大屏巨匣。',
         phone='138****8911', email='zhangts@qianqi.cn',
         level='国家级', craft='雕漆', years=48, intro='刀笔刻石，漆光映陇', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage23', role='heritage', name='卫连升', nick='凤翔罩金',
         gender='男', region='陕西省宝鸡市凤翔区', bio='凤翔罩金漆器传人，金箔封于漆里、日久愈亮，屏柜插屏为长。',
         phone='138****8912', email='weibj@qianqi.cn',
         level='省级', craft='罩金漆器', years=31, intro='金在漆里，愈久愈亮', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage24', role='heritage', name='郝广田', nick='廊坊雕填',
         gender='男', region='河北省廊坊市广阳区', bio='廊坊宫廷漆艺传人，雕填、脱胎、金漆镶嵌皆承京作一脉。',
         phone='138****8913', email='hao@qianqi.cn',
         level='省级', craft='雕填漆器', years=36, intro='京漆南播，廊坊成林', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage25', role='heritage', name='付国芳', nick='廊坊脱胎',
         gender='女', region='河北省廊坊市广阳区', bio='脱胎漆器髹饰技艺传人，师承廊坊京作一脉，擅以漆布脱胎制日用漆器。',
         phone='138****8914', email='fu@qianqi.cn',
         level='省级', craft='脱胎漆器', years=29, intro='布漆成胎，日用见真章', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage26', role='heritage', name='于春华', nick='潍坊嵌银',
         gender='女', region='山东省潍坊市', bio='潍坊嵌银髹漆技艺传人，银丝入木、髹漆相守，盘匣笔筒为上。',
         phone='138****8915', email='yu@qianqi.cn',
         level='国家级', craft='嵌银髹漆', years=33, intro='银丝走线，漆木同心', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage27', role='heritage', name='王伯林', nick='桂山天然胎',
         gender='男', region='广西壮族自治区桂林市', bio='桂林漆器传人，以竹根、柚壳、葫芦等天然胎髹漆，「以象制器」。',
         phone='138****8916', email='wanggl@qianqi.cn',
         level='省级', craft='天然胎漆器', years=30, intro='借物成形，顺其自然', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage28', role='heritage', name='杨清涧', nick='海上漆家',
         gender='女', region='上海市闵行区', bio='上海漆器制作技艺传人，兼长平磨螺钿与雕漆嵌玉，器风精细。',
         phone='138****8917', email='yangsh@qianqi.cn',
         level='市级', craft='平磨螺钿', years=35, intro='海上生明月，漆器照人清', honor='上海市非遗代表性传承人', status='active'),
    dict(username='heritage29', role='heritage', name='尹治平', nick='阳江漆客',
         gender='男', region='广东省阳江市', bio='阳江漆器髹饰技艺传人，以腰果漆髹涂日用漆器，耐潮耐热。',
         phone='138****8918', email='yin@qianqi.cn',
         level='国家级', craft='髹漆', years=39, intro='腰果成漆，器走南洋', honor='国家级非遗代表性传承人', status='active'),
    dict(username='heritage30', role='heritage', name='陈静芳', nick='潮汕金漆画',
         gender='女', region='广东省揭阳市普宁市', bio='普宁铁笔金漆画传人，黑漆推光板上描金刻线，神龛屏风多见。',
         phone='138****8919', email='chenjy@qianqi.cn',
         level='省级', craft='金漆画', years=27, intro='铁笔走金，暗室生辉', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage31', role='heritage', name='岩罕章', nick='耿马傣漆',
         gender='男', region='云南省临沧市耿马县', bio='傣族漆器制作技艺传人，竹篾编胎髹漆彩绘，红黑金三色龙凤纹。',
         phone='138****8920', email='yan@qianqi.cn',
         level='省级', craft='髹漆', years=29, intro='竹骨漆身，傣家瑰宝', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage32', role='heritage', name='徐广昭', nick='昭通漆刻',
         gender='男', region='云南省昭通市', bio='昭通漆刻传人，以刀在漆面剔刻花鸟人物，再填彩晕染，成品如画。',
         phone='138****8921', email='xu@qianqi.cn',
         level='省级', craft='漆刻', years=33, intro='刻漆如纸，填彩如画', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage33', role='heritage', name='苏婉晴', nick='雪原漆嵌',
         gender='女', region='黑龙江省哈尔滨市', bio='金漆镶嵌工艺传人，承京作金漆镶嵌一脉，擅把北地冰雪意象融进镶嵌髹饰。',
         phone='138****8922', email='su@qianqi.cn',
         level='省级', craft='金漆镶嵌', years=31, intro='北地漆语，冰雪为魂', honor='省级非遗代表性传承人', status='active'),
    dict(username='heritage34', role='heritage', name='刘东篱', nick='怀府纻器',
         gender='男', region='河南省焦作市沁阳市', bio='野王纻器制作技艺传人，麻布漆灰层层夹纻，为脱胎漆器之先声。',
         phone='138****8923', email='liuhn@qianqi.cn',
         level='省级', craft='夹纻纻器', years=35, intro='纻胎千年，麻布成器', honor='省级非遗代表性传承人', status='active'),
    dict(username='user01', role='user', name='余老板', nick='漆艺发烧友',
         gender='男', region='四川省成都市', bio='经营一间茶室，喜欢收藏漆器，也爱亲手体验髹漆。',
         phone='138****1234', email='yu@qianqi.cn',
         level='', craft='', years=None, intro='一盏一纹，各有性情', honor='', status='active'),
    dict(username='user02', role='user', name='林小雨', nick='小雨爱漆器',
         gender='女', region='江苏省扬州市', bio='非遗方向在读研究生，关注漆器技艺的当代传承。',
         phone='139****5678', email='lin@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user03', role='user', name='唐一苇', nick='苇编漆缘',
         gender='男', region='浙江省杭州市', bio='设计师，想把大漆与日用器物结合，常来线下工作坊取经。',
         phone='137****9988', email='tang@qianqi.cn',
         level='', craft='', years=None, intro='器物有魂，漆有其光', honor='', status='active'),
    dict(username='user04', role='user', name='顾青梧', nick='梧桐漆舍',
         gender='女', region='北京市海淀区', bio='文创店主理人，精选各地传承人漆器作品上架自营小店。',
         phone='136****7766', email='gu@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user05', role='user', name='杨柳', nick='杨柳依依',
         gender='女', region='福建省福州市', bio='体验课后迷上髹漆，周末常来工坊。',
         phone='133****2211', email='yang@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user06', role='user', name='王木生', nick='木生漆作',
         gender='男', region='福建省福州市', bio='木工出身，想把榫卯与漆器结合。',
         phone='137****3456', email='wang@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user07', role='user', name='吴青', nick='青衫漆客',
         gender='男', region='浙江省温州市', bio='做茶器生意，喜欢素色漆器。',
         phone='132****4455', email='wu@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user08', role='user', name='徐伯安', nick='半盏茶',
         gender='男', region='江苏省南京市', bio='经营茶室，为自家漆器做保养而来。',
         phone='138****5566', email='xu@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user09', role='user', name='高启铭', nick='铭记漆坊',
         gender='男', region='福建省厦门市', bio='体验课结业后续报系统课程。',
         phone='136****2211', email='gao@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user10', role='user', name='陈秋白', nick='秋白一漆',
         gender='男', region='江苏省扬州市', bio='关注扬州漆器的传统髹饰工艺。',
         phone='135****9012', email='chen@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user11', role='user', name='赵一鸣', nick='一鸣雕漆',
         gender='男', region='北京市朝阳区', bio='有雕漆基础，来补足髹漆全流程。',
         phone='136****7890', email='zhao@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user12', role='user', name='周小雅', nick='小雅漆记',
         gender='女', region='上海市黄浦区', bio='体验课之后转系统班，喜欢描金。',
         phone='133****2233', email='zhou@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user13', role='user', name='郑盈盈', nick='盈盈漆舍',
         gender='女', region='广东省广州市', bio='刚入门，正在学打底与推光。',
         phone='137****8822', email='zheng@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user14', role='user', name='罗嘉', nick='嘉木漆缘',
         gender='男', region='四川省成都市', bio='木作爱好者，想自己做一件脱胎漆器。',
         phone='139****4455', email='luo@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user15', role='user', name='何文远', nick='文远雕刀',
         gender='男', region='河北省廊坊市', bio='专程来学北派雕漆刀法。',
         phone='150****1122', email='he@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user16', role='user', name='孙雪', nick='雪庐漆事',
         gender='女', region='北京市海淀区', bio='美术专业在读，研究漆画语言。',
         phone='151****6677', email='sun@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user17', role='user', name='方奕', nick='方寸漆心',
         gender='男', region='天津市和平区', bio='雕刻零基础，从刀法班开始学。',
         phone='158****3344', email='fang@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
    dict(username='user18', role='user', name='许蔚然', nick='蔚然漆风',
         gender='女', region='山东省济南市', bio='想系统学习雕漆，为工作室储备技艺。',
         phone='159****8899', email='xu2@qianqi.cn',
         level='', craft='', years=None, intro='', honor='', status='active'),
]

PROFILES = [
    dict(username='heritage01', name='张守一', gender='男', age=58, phone='138****8888',
         mentor='师承川派漆艺名宿王老', years=40, level='国家级', craft='髹漆·镏金',
         honors='省级非遗代表性传承人｜作品入藏中国国家博物馆',
         intro='髹漆四十余年，师承川派漆艺，门下弟子遍及南北，常年在成都开设髹漆工作坊。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage02', name='赵雕', gender='男', age=49, phone='138****8889',
         mentor='师承北派雕漆传人', years=22, level='国家级', craft='雕漆',
         honors='全国工艺美术展览金奖',
         intro='师承北派雕漆传人，擅长剔犀云纹与剔红，刀法利落，开设雕漆系统刀法课程。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage03', name='姚镜春', gender='女', age=52, phone='138****8892',
         mentor='师承京作金漆镶嵌世家', years=30, level='国家级', craft='金漆镶嵌',
         honors='京作漆器精品展金奖',
         intro='传承京作金漆镶嵌髹饰技艺，主攻百宝嵌与玉石镶嵌漆器。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage04', name='郑寿山', gender='男', age=58, phone='138****8893',
         mentor='平遥推光漆世家传习', years=36, level='国家级', craft='推光漆',
         honors='山西省工艺美术大师',
         intro='以平遥推光漆器为业，手掌推光一脉相承，坚守「髹漆—推光」古法。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage05', name='卫子谦', gender='男', age=54, phone='138****8894',
         mentor='绛州剔犀世家祖传', years=34, level='国家级', craft='剔犀',
         honors='山西省工艺美术大师',
         intro='绛州剔犀世家出身，专攻云纹剔犀（云雕），刀口层色分明。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage06', name='李爱华', gender='女', age=62, phone='138****8895',
         mentor='师承软螺钿镶嵌名家', years=40, level='国家级', craft='螺钿',
         honors='中国工艺美术百花奖优秀奖',
         intro='以软螺钿镶嵌漆器见长，贝片薄如蝉翼，嵌花温润流光。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage07', name='沈砚秋', gender='女', age=54, phone='138****8896',
         mentor='师承扬州漆器髹饰名家', years=32, level='国家级', craft='扬州漆器',
         honors='江苏省工艺美术名人',
         intro='扬州漆器髹饰技艺传人，兼习点螺、平磨螺钿与雕漆嵌玉诸法。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage08', name='温知远', gender='男', age=56, phone='138****8897',
         mentor='师承吴门款彩老艺人', years=33, level='省级', craft='款彩',
         honors='江苏省工艺美术大师',
         intro='专研苏州漆器款彩（刻灰填彩）与素髹揩漆，屏风挂屏一绝。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage09', name='梁福宁', gender='女', age=66, phone='138****8898',
         mentor='师承福州脱胎漆器世家', years=46, level='国家级', craft='脱胎漆器',
         honors='中国工艺美术大师',
         intro='福州脱胎漆器髹饰技艺传人，脱胎成器、轻巧坚固，长于闪光髹饰。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage10', name='蔡水镜', gender='男', age=64, phone='138****8899',
         mentor='师承厦门漆线雕老艺人', years=44, level='国家级', craft='漆线雕',
         honors='福建省工艺美术大师',
         intro='厦门漆线雕技艺传人，捻线盘绕、贴金庄严，专攻神佛造像装饰。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage11', name='林正源', gender='男', age=48, phone='138****8900',
         mentor='师承泉州漆线雕名家', years=28, level='省级', craft='漆线雕',
         honors='泉州市工艺美术大师',
         intro='承泉州漆线雕与永春漆篮两艺，竹篮髹漆、堆雕彩绘皆通。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage12', name='童启山', gender='男', age=72, phone='138****8901',
         mentor='师承天台山干漆夹苎艺人', years=52, level='国家级', craft='夹苎脱胎',
         honors='国家级非遗代表性传承人',
         intro='天台山干漆夹苎技艺传人，以漆麻裱塑佛像，兼擅临海犀皮漆艺。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage13', name='何元章', gender='男', age=61, phone='138****8902',
         mentor='师承宁波泥金彩漆世家', years=41, level='国家级', craft='泥金彩漆',
         honors='浙江省工艺美术大师',
         intro='传宁波泥金彩漆与朱金漆木雕，漆金并重，曾为十里红妆髹嫁奁。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage14', name='吴乐清', gender='女', age=58, phone='138****8903',
         mentor='师承平阳漆器髹饰艺人', years=39, level='省级', craft='平阳漆器',
         honors='温州市非遗代表性传承人',
         intro='平阳漆器制作技艺传人，髹涂推光、日用陈设皆善，一脉承宋元温州漆器遗风。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage15', name='甘玉成', gender='男', age=58, phone='138****8904',
         mentor='师承徽州髹漆老匠人', years=37, level='国家级', craft='犀皮漆',
         honors='安徽省工艺美术大师',
         intro='徽州漆器髹饰技艺传人，擅犀皮（菠萝漆）与漆砂砚，恢复古法打埝起纹。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage16', name='邹槐安', gender='男', age=63, phone='138****8905',
         mentor='师承荆州髹漆修复名家', years=43, level='国家级', craft='髹漆彩绘',
         honors='湖北省工艺美术大师',
         intro='楚式漆器髹饰技艺传人，髹漆彩绘楚风纹样，兼事出土漆木器修复。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage17', name='陈其梁', gender='男', age=60, phone='138****8906',
         mentor='坝漆世家祖传', years=41, level='国家级', craft='制漆',
         honors='利川坝漆技艺代表性传承人',
         intro='利川坝漆割漆制漆传人，「坝漆名冠全球」之乡的生漆匠。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage18', name='龙漫', gender='女', age=58, phone='138****8907',
         mentor='师承重庆漆器髹饰名家', years=38, level='国家级', craft='研磨彩绘',
         honors='重庆市工艺美术大师',
         intro='重庆漆器髹饰技艺传人，长于研磨彩绘与堆漆研磨，漆面沉静多变。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage19', name='吉伍阿依', gender='女', age=62, phone='138****8908',
         mentor='彝族漆器世家族内传习', years=46, level='国家级', craft='彝族漆器',
         honors='四川省非遗代表性传承人',
         intro='彝族漆器髹饰技艺传人，黑红黄三色手绘，纹样取自日月山川。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage20', name='高小梅', gender='女', age=60, phone='138****8909',
         mentor='师承大方漆器髹漆艺人', years=44, level='国家级', craft='彝族漆器',
         honors='贵州省工艺美术大师',
         intro='贵州大方彝族漆器传人，皮木胎髹漆彩绘，漆器经久耐用。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage21', name='周子萍', gender='女', age=55, phone='138****8910',
         mentor='师承鄱阳脱胎漆器世家', years=35, level='国家级', craft='脱胎漆器',
         honors='江西省工艺美术大师',
         intro='鄱阳脱胎漆器髹饰技艺传人，脱胎胎薄如纸、坚如瓷，兼研婺源菠萝漆。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage22', name='张铁山', gender='男', age=68, phone='138****8911',
         mentor='师承天水雕漆老匠人', years=48, level='国家级', craft='雕漆',
         honors='甘肃省工艺美术大师',
         intro='天水雕漆传人，以雕填、石刻镶嵌与彩绘见长，擅作大屏巨匣。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage23', name='卫连升', gender='男', age=52, phone='138****8912',
         mentor='师承凤翔罩金漆器艺人', years=31, level='省级', craft='罩金漆器',
         honors='陕西省工艺美术大师',
         intro='凤翔罩金漆器传人，金箔封于漆里、日久愈亮，屏柜插屏为长。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage24', name='郝广田', gender='男', age=56, phone='138****8913',
         mentor='师承京作漆艺传入廊坊一脉', years=36, level='省级', craft='雕填漆器',
         honors='河北省非遗代表性传承人',
         intro='廊坊宫廷漆艺传人，雕填、脱胎、金漆镶嵌皆承京作一脉。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage25', name='付国芳', gender='女', age=48, phone='138****8914',
         mentor='师承廊坊脱胎髹饰艺人', years=29, level='省级', craft='脱胎漆器',
         honors='廊坊市非遗代表性传承人',
         intro='脱胎漆器髹饰技艺传人，师承廊坊京作一脉，擅以漆布脱胎制日用漆器。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage26', name='于春华', gender='女', age=54, phone='138****8915',
         mentor='师承潍坊嵌银髹漆世家', years=33, level='国家级', craft='嵌银髹漆',
         honors='山东省工艺美术大师',
         intro='潍坊嵌银髹漆技艺传人，银丝入木、髹漆相守，盘匣笔筒为上。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage27', name='王伯林', gender='男', age=52, phone='138****8916',
         mentor='师承桂林天然胎漆器艺人', years=30, level='省级', craft='天然胎漆器',
         honors='广西工艺美术大师',
         intro='桂林漆器传人，以竹根、柚壳、葫芦等天然胎髹漆，「以象制器」。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage28', name='杨清涧', gender='女', age=55, phone='138****8917',
         mentor='师承上海髹漆镶嵌名家', years=35, level='市级', craft='平磨螺钿',
         honors='上海市非遗代表性传承人',
         intro='上海漆器制作技艺传人，兼长平磨螺钿与雕漆嵌玉，器风精细。',
         qual='市级非遗代表性传承人', status='active'),
    dict(username='heritage29', name='尹治平', gender='男', age=58, phone='138****8918',
         mentor='师承阳江漆器髹饰艺人', years=39, level='国家级', craft='髹漆',
         honors='广东省工艺美术大师',
         intro='阳江漆器髹饰技艺传人，以腰果漆髹涂日用漆器，耐潮耐热。',
         qual='国家级非遗代表性传承人', status='active'),
    dict(username='heritage30', name='陈静芳', gender='女', age=46, phone='138****8919',
         mentor='师承普宁铁笔金漆画艺人', years=27, level='省级', craft='金漆画',
         honors='揭阳市非遗代表性传承人',
         intro='普宁铁笔金漆画传人，黑漆推光板上描金刻线，神龛屏风多见。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage31', name='岩罕章', gender='男', age=50, phone='138****8920',
         mentor='傣族漆器家族传习', years=29, level='省级', craft='髹漆',
         honors='临沧市非遗代表性传承人',
         intro='傣族漆器制作技艺传人，竹篾编胎髹漆彩绘，红黑金三色龙凤纹。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage32', name='徐广昭', gender='男', age=55, phone='138****8921',
         mentor='师承昭通漆刻老艺人', years=33, level='省级', craft='漆刻',
         honors='云南省非遗代表性传承人',
         intro='昭通漆刻传人，以刀在漆面剔刻花鸟人物，再填彩晕染，成品如画。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage33', name='苏婉晴', gender='女', age=52, phone='138****8922',
         mentor='师承京作金漆镶嵌北传一脉', years=31, level='省级', craft='金漆镶嵌',
         honors='黑龙江省非遗代表性传承人',
         intro='金漆镶嵌工艺传人，承京作一脉，擅将北地冰雪意象融入镶嵌髹饰。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username='heritage34', name='刘东篱', gender='男', age=55, phone='138****8923',
         mentor='师承沁阳纻器艺人', years=35, level='省级', craft='纻器夹纻',
         honors='河南省非遗代表性传承人',
         intro='野王纻器制作技艺传人，麻布漆灰层层夹纻，为脱胎漆器之先声。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username=None, name='钱螺', gender='女', age=42, phone='138****8890',
         mentor='师承螺钿镶嵌世家', years=18, level='省级', craft='螺钿',
         honors='非遗文创设计大赛银奖', intro='专注螺钿镶嵌，作品精致典雅。',
         qual='省级非遗代表性传承人', status='active'),
    dict(username=None, name='周金', gender='女', age=39, phone='138****8891',
         mentor='师承描金画派传人', years=15, level='市级', craft='描金',
         honors='', intro='专攻描金漆画，线条细腻。',
         qual='市级非遗代表性传承人', status='leave'),
]

ORDERS = [
    dict(type='product', item_name='犀皮描金茶盏', glyph='盏', buyer='余老板', buyer_phone='138****1234',
         price=368, status='paid', pay_method='微信支付', order_time='2026-08-30 20:14', pay_time='2026-08-30 20:15',
         receiver='余老板', address='四川省成都市锦江区某某路 88 号', phone='138****1234', remark='请轻拿轻放，谢谢。',
         seller_username='heritage01', buyer_username='user01'),
    dict(type='product', item_name='犀皮描金茶盏', glyph='盏', buyer='王木生', buyer_phone='137****3456',
         price=368, status='paid', pay_method='微信支付', order_time='2026-08-31 09:20', pay_time='2026-08-31 09:22',
         receiver='王木生', address='北京市东城区某某胡同 3 号', phone='137****3456', remark='',
         seller_username='heritage01', buyer_username=None),
    dict(type='product', item_name='雕漆云纹果盘', glyph='盘', buyer='陈秋白', buyer_phone='135****9012',
         price=588, status='shipped', pay_method='支付宝', order_time='2026-08-29 16:42', pay_time='2026-08-29 16:43',
         receiver='陈秋白', address='江苏省扬州市广陵区某某街 12 号', phone='135****9012', remark='',
         company='顺丰速运', tracking_no='SF20260829001', ship_time='2026-08-29 18:20',
         seller_username='heritage02', buyer_username=None),
    dict(type='product', item_name='雕漆云纹果盘', glyph='盘', buyer='赵一鸣', buyer_phone='136****7890',
         price=588, status='pending', pay_method='', order_time='2026-09-01 09:05', pay_time='',
         receiver='赵一鸣', address='北京市朝阳区某某小区 6 号楼', phone='136****7890', remark='希望作为礼物，麻烦包装精美一些。',
         seller_username='heritage02', buyer_username=None),
    dict(type='product', item_name='犀皮描金茶盏', glyph='盏', buyer='林小雨', buyer_phone='139****5678',
         price=368, status='cancelled', pay_method='微信支付', order_time='2026-08-27 20:00', pay_time='2026-08-27 20:02',
         receiver='', address='', phone='', remark='重复下单，申请取消退款。',
         seller_username='heritage01', buyer_username='user02'),
    dict(type='course', item_name='半日髹漆体验 · 素色茶碗', glyph='课', buyer='余老板', buyer_phone='138****1234',
         price=198, status='done', pay_method='支付宝', order_time='2026-08-08 09:03', pay_time='2026-08-08 09:05',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username='user01'),
    dict(type='course', item_name='半日髹漆体验 · 素色茶碗', glyph='课', buyer='林小雨', buyer_phone='139****5678',
         price=198, status='paid', pay_method='支付宝', order_time='2026-08-28 10:18', pay_time='2026-08-28 10:20',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username='user02'),
    dict(type='course', item_name='髹漆系统课程 · 基础班', glyph='课', buyer='陈秋白', buyer_phone='135****9012',
         price=980, status='paid', pay_method='微信支付', order_time='2026-08-20 11:20', pay_time='2026-08-20 11:22',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username=None),
    dict(type='course', item_name='髹漆系统课程 · 基础班', glyph='课', buyer='赵一鸣', buyer_phone='136****7890',
         price=980, status='paid', pay_method='支付宝', order_time='2026-08-30 15:10', pay_time='2026-08-30 15:12',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username=None),
    dict(type='course', item_name='雕漆系统课程 · 刀法班', glyph='课', buyer='何文远', buyer_phone='150****1122',
         price=1280, status='paid', pay_method='支付宝', order_time='2026-09-01 14:30', pay_time='2026-09-01 14:32',
         receiver='', address='', phone='', remark='',
         seller_username='heritage02', buyer_username=None),
    dict(type='product', item_name='推光漆 · 描金缠枝首饰匣', glyph='匣', buyer='顾青梧', buyer_phone='136****7766',
         price=980, status='paid', pay_method='微信支付', order_time='2026-09-02 12:30', pay_time='2026-09-02 12:32',
         receiver='顾青梧', address='北京市海淀区某某大厦 2 层', phone='136****7766', remark='自营小店首批上架，请附证书。',
         seller_username='heritage04', buyer_username='user04'),
    dict(type='product', item_name='推光漆 · 描金缠枝首饰匣', glyph='匣', buyer='徐伯安', buyer_phone='138****5566',
         price=980, status='done', pay_method='支付宝', order_time='2026-09-02 14:00', pay_time='2026-09-02 14:03',
         receiver='徐伯安', address='四川省绵阳市涪城区某某路 9 号', phone='138****5566', remark='',
         seller_username='heritage04', buyer_username=None),
    dict(type='product', item_name='脱胎漆器 · 蝉纹主人杯', glyph='杯', buyer='林小雨', buyer_phone='139****5678',
         price=1280, status='paid', pay_method='微信支付', order_time='2026-09-02 15:10', pay_time='2026-09-02 15:12',
         receiver='林小雨', address='江苏省扬州市广陵区某某街 12 号', phone='139****5678', remark='',
         seller_username='heritage09', buyer_username='user02'),
    dict(type='product', item_name='脱胎漆器 · 蝉纹主人杯', glyph='杯', buyer='唐一苇', buyer_phone='137****9988',
         price=1280, status='pending', pay_method='', order_time='2026-09-03 09:30', pay_time='',
         receiver='唐一苇', address='浙江省杭州市西湖区某某路 5 号', phone='137****9988', remark='',
         seller_username='heritage09', buyer_username='user03'),
    dict(type='product', item_name='点螺 · 千里江山茶台', glyph='台', buyer='顾青梧', buyer_phone='136****7766',
         price=3280, status='done', pay_method='银行转账', order_time='2026-08-31 11:00', pay_time='2026-08-31 11:20',
         receiver='顾青梧', address='北京市海淀区某某大厦 2 层', phone='136****7766', remark='作小店镇店之宝。',
         company='顺丰速运', tracking_no='SF20260831001', ship_time='2026-08-31 16:00',
         seller_username='heritage07', buyer_username='user04'),
    dict(type='product', item_name='犀皮漆 · 云纹主人杯', glyph='杯', buyer='余老板', buyer_phone='138****1234',
         price=1280, status='shipped', pay_method='支付宝', order_time='2026-09-02 17:00', pay_time='2026-09-02 17:02',
         receiver='余老板', address='四川省成都市锦江区某某路 88 号', phone='138****1234', remark='',
         company='中通快递', tracking_no='ZTO20260902001', ship_time='2026-09-03 09:00',
         seller_username='heritage15', buyer_username='user01'),
    dict(type='product', item_name='楚式漆器 · 凤鸟纹圆奁盒', glyph='奁', buyer='陈秋白', buyer_phone='135****9012',
         price=1580, status='pending', pay_method='', order_time='2026-09-03 10:00', pay_time='',
         receiver='陈秋白', address='江苏省扬州市广陵区某某街 12 号', phone='135****9012', remark='',
         seller_username='heritage16', buyer_username=None),
    dict(type='product', item_name='软螺钿 · 缠枝莲纹盘', glyph='盘', buyer='唐一苇', buyer_phone='137****9988',
         price=880, status='paid', pay_method='微信支付', order_time='2026-09-02 19:20', pay_time='2026-09-02 19:21',
         receiver='唐一苇', address='浙江省杭州市西湖区某某路 5 号', phone='137****9988', remark='',
         seller_username='heritage06', buyer_username='user03'),
    dict(type='product', item_name='剔犀 · 如意云纹执壶', glyph='壶', buyer='赵一鸣', buyer_phone='136****7890',
         price=1680, status='shipped', pay_method='支付宝', order_time='2026-09-01 20:10', pay_time='2026-09-01 20:12',
         receiver='赵一鸣', address='北京市朝阳区某某小区 6 号楼', phone='136****7890', remark='',
         company='京东物流', tracking_no='JD20260901001', ship_time='2026-09-02 10:00',
         seller_username='heritage05', buyer_username=None),
    dict(type='product', item_name='嵌银髹漆 · 紫檀笔筒', glyph='筒', buyer='郑盈盈', buyer_phone='137****8822',
         price=1180, status='pending', pay_method='', order_time='2026-09-03 08:40', pay_time='',
         receiver='郑盈盈', address='山东省青岛市市南区某某路 18 号', phone='137****8822', remark='',
         seller_username='heritage26', buyer_username=None),
    dict(type='product', item_name='雕漆 · 青绿山水挂屏', glyph='屏', buyer='吴青', buyer_phone='132****4455',
         price=3280, status='done', pay_method='银行转账', order_time='2026-08-30 10:00', pay_time='2026-08-30 10:30',
         receiver='吴青', address='陕西省西安市雁塔区某某园 3 单元', phone='132****4455', remark='新居客厅陈列。',
         company='顺丰速运', tracking_no='SF20260830002', ship_time='2026-08-30 15:00',
         seller_username='heritage22', buyer_username=None),
    dict(type='product', item_name='阳江漆器 · 提梁食盒', glyph='盒', buyer='王木生', buyer_phone='137****3456',
         price=680, status='paid', pay_method='微信支付', order_time='2026-09-02 21:00', pay_time='2026-09-02 21:02',
         receiver='王木生', address='北京市东城区某某胡同 3 号', phone='137****3456', remark='',
         seller_username='heritage29', buyer_username=None),
    dict(type='course', item_name='半日髹漆体验 · 素色茶碗', glyph='课', buyer='徐伯安', buyer_phone='138****5566',
         price=198, status='done', pay_method='微信支付', order_time='2026-09-01 10:28', pay_time='2026-09-01 10:30',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username=None),
    dict(type='course', item_name='半日髹漆体验 · 素色茶碗', glyph='课', buyer='高启铭', buyer_phone='136****2211',
         price=198, status='done', pay_method='支付宝', order_time='2026-08-22 13:58', pay_time='2026-08-22 14:00',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username=None),
    dict(type='course', item_name='髹漆系统课程 · 基础班', glyph='课', buyer='郑盈盈', buyer_phone='137****8822',
         price=980, status='paid', pay_method='支付宝', order_time='2026-09-01 09:38', pay_time='2026-09-01 09:40',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username=None),
    dict(type='course', item_name='髹漆系统课程 · 基础班', glyph='课', buyer='罗嘉', buyer_phone='139****4455',
         price=980, status='paid', pay_method='微信支付', order_time='2026-08-31 16:18', pay_time='2026-08-31 16:20',
         receiver='', address='', phone='', remark='',
         seller_username='heritage01', buyer_username=None),
    dict(type='course', item_name='雕漆系统课程 · 刀法班', glyph='课', buyer='方奕', buyer_phone='158****3344',
         price=1280, status='paid', pay_method='支付宝', order_time='2026-09-02 10:08', pay_time='2026-09-02 10:10',
         receiver='', address='', phone='', remark='',
         seller_username='heritage02', buyer_username=None),
    dict(type='course', item_name='雕漆系统课程 · 刀法班', glyph='课', buyer='许蔚然', buyer_phone='159****8899',
         price=1280, status='paid', pay_method='微信支付', order_time='2026-09-02 10:58', pay_time='2026-09-02 11:00',
         receiver='', address='', phone='', remark='',
         seller_username='heritage02', buyer_username=None),
]

STUDENTS = [
    dict(name='余老板', phone='138****1234', avatar_glyph='余', username='user01',
         course_name='半日髹漆体验 · 素色茶碗', teacher='张守一', craft='髹漆', price=198,
         enroll_time='2026-08-08 09:05', status='done', progress=100, note='已结课，作品素色茶碗已带走'),
    dict(name='杨柳', phone='133****2211', avatar_glyph='杨', username='user05',
         course_name='半日髹漆体验 · 素色茶碗', teacher='张守一', craft='髹漆', price=198,
         enroll_time='2026-08-08 09:12', status='done', progress=90, note=''),
    dict(name='林小雨', phone='139****5678', avatar_glyph='林', username='user02',
         course_name='半日髹漆体验 · 素色茶碗', teacher='张守一', craft='髹漆', price=198,
         enroll_time='2026-08-28 10:20', status='ongoing', progress=40, note='零基础学员，上手很快'),
    dict(name='王木生', phone='137****3456', avatar_glyph='王', username='user06',
         course_name='半日髹漆体验 · 素色茶碗', teacher='张守一', craft='髹漆', price=198,
         enroll_time='2026-08-29 10:10', status='ongoing', progress=20, note=''),
    dict(name='吴青', phone='132****4455', avatar_glyph='吴', username='user07',
         course_name='半日髹漆体验 · 素色茶碗', teacher='张守一', craft='髹漆', price=198,
         enroll_time='2026-08-25 11:08', status='ongoing', progress=60, note='希望课后带走未完成的作品继续打磨'),
    dict(name='徐伯安', phone='138****5566', avatar_glyph='徐', username='user08',
         course_name='半日髹漆体验 · 素色茶碗', teacher='张守一', craft='髹漆', price=198,
         enroll_time='2026-09-01 10:30', status='ongoing', progress=20, note='茶室老板，想学会保养自家漆器'),
    dict(name='高启铭', phone='136****2211', avatar_glyph='高', username='user09',
         course_name='半日髹漆体验 · 素色茶碗', teacher='张守一', craft='髹漆', price=198,
         enroll_time='2026-08-22 14:00', status='done', progress=100, note='已结课，续报系统课程'),
    dict(name='陈秋白', phone='135****9012', avatar_glyph='陈', username='user10',
         course_name='髹漆系统课程 · 基础班', teacher='张守一', craft='髹漆', price=980,
         enroll_time='2026-08-20 11:22', status='ongoing', progress=55, note=''),
    dict(name='赵一鸣', phone='136****7890', avatar_glyph='赵', username='user11',
         course_name='髹漆系统课程 · 基础班', teacher='张守一', craft='髹漆', price=980,
         enroll_time='2026-08-30 15:12', status='ongoing', progress=30, note='有雕漆基础，想补足髹漆全流程'),
    dict(name='周小雅', phone='133****2233', avatar_glyph='周', username='user12',
         course_name='髹漆系统课程 · 基础班', teacher='张守一', craft='髹漆', price=980,
         enroll_time='2026-08-19 14:30', status='ongoing', progress=45, note='已上完体验课，转系统班'),
    dict(name='郑盈盈', phone='137****8822', avatar_glyph='郑', username='user13',
         course_name='髹漆系统课程 · 基础班', teacher='张守一', craft='髹漆', price=980,
         enroll_time='2026-09-01 09:40', status='ongoing', progress=15, note=''),
    dict(name='罗嘉', phone='139****4455', avatar_glyph='罗', username='user14',
         course_name='髹漆系统课程 · 基础班', teacher='张守一', craft='髹漆', price=980,
         enroll_time='2026-08-31 16:20', status='ongoing', progress=20, note=''),
    dict(name='何文远', phone='150****1122', avatar_glyph='何', username='user15',
         course_name='雕漆系统课程 · 刀法班', teacher='赵雕', craft='雕漆', price=1280,
         enroll_time='2026-09-01 14:32', status='ongoing', progress=15, note=''),
    dict(name='孙雪', phone='151****6677', avatar_glyph='孙', username='user16',
         course_name='雕漆系统课程 · 刀法班', teacher='赵雕', craft='雕漆', price=1280,
         enroll_time='2026-09-01 15:00', status='ongoing', progress=10, note=''),
    dict(name='方奕', phone='158****3344', avatar_glyph='方', username='user17',
         course_name='雕漆系统课程 · 刀法班', teacher='赵雕', craft='雕漆', price=1280,
         enroll_time='2026-09-02 10:10', status='ongoing', progress=5, note=''),
    dict(name='许蔚然', phone='159****8899', avatar_glyph='许', username='user18',
         course_name='雕漆系统课程 · 刀法班', teacher='赵雕', craft='雕漆', price=1280,
         enroll_time='2026-09-02 11:00', status='ongoing', progress=5, note=''),
]

SKILLS = [
    dict(name='成都漆艺', glyph='漆', level='国家级', category='髹漆技艺', region='四川省成都市', origin='四川成都',
         abstract='成都漆艺以雕花填彩、银片丝光、嵌彩、隐花见长，为我国西南漆艺重镇；以天然生漆髹涂，温润耐腐，历数千年不衰。',
         years=40, desc='掌握制胎、裱布、刮灰、髹涂、装饰与推光全流程，尤擅素髹与朱漆，兼通雕花填彩。',
         steps='制胎｜裱布刮灰｜多道髹涂｜雕花填彩等装饰｜打磨推光揩清',
         works='雕花填彩屏风｜银片丝光茶盒｜朱漆素髹主人杯',
         courses='半日髹漆体验 · 素色茶碗｜髹漆系统课程 · 基础班',
         status='approved', submit_time='2026-08-05 10:00', review_comment='', owner_username='heritage01'),
    dict(name='雕漆技艺', glyph='雕', level='国家级', category='雕漆', region='北京市东城区', origin='北京',
         abstract='雕漆又称剔红，须在胎上髹漆数十乃至数百道，漆层厚积后以刀代笔剔刻山水人物、花卉云纹。北京雕漆为其重要产地。',
         years=22, desc='长于剔犀云纹与剔红花卉，执刀运腕讲究深匀利落，纹样层次分明。',
         steps='髹漆累积｜设计剔稿｜执刀剔刻｜修光打磨',
         works='剔红山水瓶｜剔犀云纹盘｜剔红如意',
         courses='雕漆系统课程 · 刀法班',
         status='approved', submit_time='2026-08-20 10:00', review_comment='', owner_username='heritage02'),
    dict(name='金漆镶嵌髹饰技艺', glyph='嵌', level='国家级', category='金漆镶嵌', region='北京市东城区', origin='北京',
         abstract='金漆镶嵌是以大漆髹涂器物，再以金银、玉石、螺钿、骨木镶嵌成图的京作髹饰技艺，成品宝色内敛、富丽端庄。',
         years=30, desc='主攻百宝嵌与玉石镶嵌漆器，选料配色讲究，镶嵌面与漆地平齐光润。',
         steps='木胎制胎｜髹底漆｜描样开槽｜百宝镶嵌｜罩漆磨显',
         works='百宝嵌插屏｜玉石镶嵌提盒｜金漆地屏',
         courses='',
         status='approved', submit_time='2026-08-25 09:00', review_comment='', owner_username='heritage03'),
    dict(name='平遥推光漆器髹饰技艺', glyph='推', level='国家级', category='推光髹饰', region='山西省晋中市平遥县', origin='山西平遥',
         abstract='平遥推光漆器以手掌蘸细砖灰与发团反复推磨漆面，直至光滑如镜，再以描金彩绘、堆鼓罩漆饰之。',
         years=36, desc='坚守「髹漆—推光」古法，掌推光漆面如镜，兼习描金彩绘与堆鼓工艺。',
         steps='木胎裱布刮灰｜髹漆打磨｜手掌推光｜描金彩绘堆鼓',
         works='推光漆描金首饰匣｜描金屏风｜堆鼓罩漆挂屏',
         courses='平遥推光漆器 · 掌上推光工作坊',
         status='approved', submit_time='2026-09-02 10:00', review_comment='', owner_username='heritage04'),
    dict(name='漆器髹饰技艺（绛州剔犀技艺）', glyph='犀', level='国家级', category='剔犀', region='山西省运城市新绛县', origin='山西新绛',
         abstract='绛州剔犀（俗称云雕）于胎上交替髹涂朱黑等多色漆，趁漆将干未干时剔刻卷云纹，刀口处露出层层色带，如行云流水。',
         years=34, desc='剔犀世家出身，刀口层色分明，云纹回环流畅，作品以器具陈设见长。',
         steps='制胎｜髹涂红黑相间漆｜阴干养漆｜剔刻云纹｜修光揩清',
         works='剔犀如意云纹执壶｜云雕剔犀瓶｜云纹高足杯',
         courses='',
         status='approved', submit_time='2026-09-02 10:10', review_comment='', owner_username='heritage05'),
    dict(name='漆器髹饰技艺（稷山螺钿漆器髹饰技艺）', glyph='贝', level='国家级', category='螺钿镶嵌', region='山西省运城市稷山县', origin='山西稷山',
         abstract='稷山螺钿以产自湖海的螺蚌贝壳磨成薄片，嵌于漆面组成人物花鸟，再髹漆磨平，贝华流光、历久不脱。',
         years=40, desc='以软螺钿镶嵌见长，贝片薄如蝉翼、选料考究，嵌花温润，人物衣褶丝丝入扣。',
         steps='制胎髹底｜贝片裁磨｜描样镶嵌｜髹漆罩护｜打磨推光',
         works='软螺钿缠枝莲盘｜贝嵌人物挂屏｜螺钿果盒',
         courses='',
         status='approved', submit_time='2026-09-02 10:20', review_comment='', owner_username='heritage06'),
    dict(name='扬州漆器髹饰技艺', glyph='扬', level='国家级', category='扬州漆器', region='江苏省扬州市', origin='江苏扬州',
         abstract='扬州漆器髹饰技艺集点螺、平磨螺钿、雕漆嵌玉、刻漆、骨石镶嵌等数十种髹饰技法于一体，有「十里漆器出广陵」之誉。',
         years=32, desc='兼习点螺、平磨螺钿与雕漆嵌玉诸法，髹饰工整、光泽莹润。',
         steps='制胎｜髹底漆｜点螺/平磨｜罩漆｜打磨推光',
         works='点螺千里江山茶台｜平磨螺钿屏风｜雕漆嵌玉挂屏',
         courses='',
         status='approved', submit_time='2026-09-02 10:30', review_comment='', owner_username='heritage07'),
    dict(name='苏州漆器制作技艺', glyph='款', level='省级', category='款彩髹饰', region='江苏省苏州市姑苏区', origin='江苏苏州',
         abstract='苏州漆器以款彩（刻灰填彩）与揩漆素髹著称，屏风挂屏刻灰填彩、浓淡得宜，桌几琴案揩漆温润。',
         years=33, desc='专研款彩刻灰与素髹揩漆，刀法爽利，填彩浓淡有致。',
         steps='制胎｜髹漆做灰｜刻灰剔纹｜填彩｜罩漆揩光',
         works='款彩山水挂屏｜揩漆琴几｜素髹漆盘',
         courses='',
         status='approved', submit_time='2026-09-02 10:40', review_comment='', owner_username='heritage08'),
    dict(name='福州脱胎漆器髹饰技艺', glyph='脱', level='国家级', category='脱胎漆器', region='福建省福州市', origin='福建福州',
         abstract='福州脱胎漆器以漆裱布夹纻成胎，干后脱模，胎薄而坚、轻巧耐用，再以闪光、晕金、描金等髹饰，为福州三宝之一。',
         years=46, desc='脱胎成器经验老到，胎体轻坚；长于闪光髹饰与磨漆，漆面含蓄生辉。',
         steps='裱布夹纻｜脱胎成形｜髹漆打磨｜闪光/晕金髹饰｜揩清',
         works='脱胎蝉纹主人杯｜脱胎寿桃摆瓶｜闪光髹饰瓶',
         courses='福州脱胎漆器 · 夹纻制盏班',
         status='approved', submit_time='2026-09-02 10:50', review_comment='', owner_username='heritage09'),
    dict(name='厦门漆线雕技艺', glyph='线', level='国家级', category='漆线雕', region='福建省厦门市', origin='福建厦门',
         abstract='厦门漆线雕以陈年的砖粉、大漆与桐油捻成细漆线，盘绕堆塑成龙凤神佛纹样，再安金箔，庄严而华美。',
         years=44, desc='捻线盘绕功夫深厚，线径匀细、转折流畅，贴金庄重不火气。',
         steps='捻漆线｜起稿盘线｜堆塑成形｜贴金箔｜髹漆加固',
         works='漆线雕关帝像｜龙凤团花盘雕｜罗汉造像',
         courses='',
         status='approved', submit_time='2026-09-02 11:00', review_comment='', owner_username='heritage10'),
    dict(name='漆线雕（泉州）', glyph='闽', level='省级', category='漆线雕', region='福建省泉州市', origin='福建泉州',
         abstract='泉州漆线雕与厦门同源而异流，多用于寺庙佛像与民间陈设装饰，线与漆的运用尤重精细饱满。',
         years=28, desc='承泉州漆线雕一脉，兼通竹篮髹漆与堆雕彩绘，器与像并擅。',
         steps='捻漆线｜盘线堆塑｜髹漆｜安金彩绘',
         works='漆线雕神龛饰件｜堆彩漆篮｜漆线狮像',
         courses='',
         status='approved', submit_time='2026-09-02 11:10', review_comment='', owner_username='heritage11'),
    dict(name='天台山干漆夹苎技艺', glyph='苎', level='国家级', category='夹苎脱胎', region='浙江省台州市天台县', origin='浙江天台',
         abstract='天台山干漆夹苎以漆与苎麻裱褙成型塑像，历久不坏，多用于佛教造像，塑像轻坚不朽、千年如新。',
         years=52, desc='以漆麻裱塑佛像数十载，夹苎层叠匀密，髹漆贴金法相庄严。',
         steps='塑胎模｜漆麻裱褙｜夹苎成型｜髹漆上彩｜贴金',
         works='干漆夹苎水月观音｜夹苎罗汉像｜夹苎香炉',
         courses='',
         status='approved', submit_time='2026-09-02 11:20', review_comment='', owner_username='heritage12'),
    dict(name='宁波泥金彩漆', glyph='泥', level='国家级', category='泥金彩漆', region='浙江省宁波市', origin='浙江宁波（宁海）',
         abstract='泥金彩漆属宁波传统髹漆装饰，于木胎髹朱漆后以油灰堆塑隆起纹样，再贴金罩漆，为「十里红妆」嫁妆家具的主要装饰。',
         years=41, desc='漆金并重，堆塑浮雕饱满，泥金匀亮，曾为十里红妆髹嫁奁。',
         steps='木胎打底｜髹朱漆｜堆塑(堆漆)｜泥金描金｜罩漆',
         works='泥金彩漆嫁奁提桶｜堆塑果盒｜彩漆妆奁',
         courses='',
         status='approved', submit_time='2026-09-02 11:30', review_comment='', owner_username='heritage13'),
    dict(name='宁波朱金漆木雕', glyph='木', level='国家级', category='朱金漆木雕', region='浙江省宁波市', origin='浙江宁波（鄞州）',
         abstract='朱金漆木雕是在木雕构件上髹朱漆、贴金箔，朱金辉映，多用于建筑装饰与家具，是宁波传统美术代表。',
         years=38, desc='漆金相济，木雕打底后髹漆贴金，层次富丽，精于花板与家具髹饰。',
         steps='木雕成型｜打磨底漆｜髹朱漆｜贴金箔｜罩护揩清',
         works='朱金漆木雕花板｜千工床构件｜贴金神像座屏',
         courses='',
         status='approved', submit_time='2026-09-02 11:40', review_comment='', owner_username='heritage13'),
    dict(name='平阳漆器制作技艺', glyph='瓯', level='省级', category='髹漆装饰', region='浙江省温州市平阳县', origin='浙江温州（平阳）',
         abstract='温州古称「漆器之乡」，平阳漆器承宋元温州髹漆遗风，器物以日用陈设居多，髹涂精致、纹饰雅正。',
         years=39, desc='髹涂推光、日用陈设皆善，作品追求宋韵古雅。',
         steps='制胎｜髹涂底漆｜纹饰髹绘｜罩漆打磨',
         works='平阳漆器提盒｜素髹茶盘｜描漆妆匣',
         courses='',
         status='approved', submit_time='2026-09-02 11:50', review_comment='', owner_username='heritage14'),
    dict(name='徽州漆器髹饰技艺', glyph='徽', level='国家级', category='犀皮漆', region='安徽省黄山市屯溪区', origin='安徽徽州（屯溪）',
         abstract='徽州漆器以犀皮（菠萝漆）、漆砂砚等著称；犀皮以稠漆打埝、层髹色漆后磨显，纹如行云流水，天然无重复。',
         years=37, desc='恢复古法打埝起纹，犀皮纹理回旋流畅；亦擅髹漆制砚。',
         steps='制胎｜打埝起纹｜层髹色漆｜研磨显纹｜揩清推光',
         works='犀皮云纹主人杯｜漆砂砚｜菠萝漆茶台',
         courses='徽州犀皮漆 · 打埝磨显班',
         status='approved', submit_time='2026-09-02 12:00', review_comment='', owner_username='heritage15'),
    dict(name='楚式漆器髹饰技艺', glyph='楚', level='国家级', category='髹漆彩绘', region='湖北省荆州市', origin='湖北荆州',
         abstract='楚式漆器承春秋战国楚文化遗风，朱黑相髹、彩绘凤鸟卷云纹样，造型自由奔放，出土楚器逾两千年仍鲜艳如新。',
         years=43, desc='髹漆彩绘楚风纹样得心应手，兼事出土漆木器修复，纹样考究。',
         steps='制胎｜髹朱/黑底漆｜彩绘描漆｜罩漆揩清',
         works='楚式凤鸟纹圆奁盒｜楚风彩绘漆盘｜虎座凤架鼓模型',
         courses='楚风漆器 · 髹绘工作坊',
         status='approved', submit_time='2026-09-02 12:10', review_comment='', owner_username='heritage16'),
    dict(name='制漆技艺（坝漆制作技艺）', glyph='坝', level='国家级', category='生漆采割精制', region='湖北省恩施州利川市', origin='湖北利川（毛坝）',
         abstract='利川毛坝盛产生漆，有「坝漆名冠全球」之誉；坝漆色艳味香、燥性好，割漆、滤漆、煎漆诸法皆精。',
         years=41, desc='割漆制漆经验丰富，识漆性、辨漆质，为髹漆艺人提供上乘生漆。',
         steps='择树割漆｜收漆过滤｜煎漆精制｜贮漆养护',
         works='坝漆头刀漆｜精制大漆｜漆酚检测样',
         courses='',
         status='approved', submit_time='2026-09-02 12:20', review_comment='', owner_username='heritage17'),
    dict(name='重庆漆器髹饰技艺', glyph='渝', level='国家级', category='研磨彩绘', region='重庆市', origin='重庆',
         abstract='重庆漆器以研磨彩绘、堆漆研磨为特色，漆层随磨随显，画面沉静多变，是我国西南漆艺又一重镇。',
         years=38, desc='长于研磨彩绘与堆漆研磨，漆面经磨后层次丰富、莹润耐看。',
         steps='制胎｜髹漆打底｜研磨彩绘｜堆漆研磨｜揩清推光',
         works='研磨彩绘圆盘｜堆漆花瓶｜朱漆嵌金茶器',
         courses='',
         status='approved', submit_time='2026-09-02 12:30', review_comment='', owner_username='heritage18'),
    dict(name='彝族漆器髹饰技艺', glyph='彝', level='国家级', category='彝族漆器', region='四川省凉山州喜德县', origin='四川凉山（喜德）',
         abstract='彝族漆器以木、皮为胎，髹涂黑漆为底，以红黄二色手绘日月山川、火镰羊角等纹样，是彝族「三色文化」的载体。',
         years=46, desc='一器三色、笔意拙朴，纹样取自日月山川与彝族生活，世代相传。',
         steps='制胎｜髹黑底漆｜调红黄漆｜彩绘纹样｜罩漆',
         works='彝族漆餐具（木碗）｜彩绘鹰爪杯｜皮胎漆器酒壶',
         courses='',
         status='approved', submit_time='2026-09-02 12:40', review_comment='', owner_username='heritage19'),
    dict(name='彝族皮胎漆器制作技艺', glyph='皮', level='省级', category='彝族漆器', region='四川省凉山州美姑县', origin='四川凉山（美姑）',
         abstract='彝族皮胎漆器以牛皮、马皮鞣制为胎再髹漆彩绘，多作铠甲、箭筒与酒器，刚柔相济、存世稀少。',
         years=42, desc='皮胎鞣制与髹彩兼通，皮酒壶、护臂等器型古拙而耐用。',
         steps='鞣制皮胎｜定型｜髹黑漆｜红黄彩绘｜罩护',
         works='皮胎彩绘酒壶｜彝式漆盾｜皮铠甲片饰件',
         courses='',
         status='pending', submit_time='2026-09-02 12:45', review_comment='', owner_username='heritage19'),
    dict(name='彝族漆器髹饰技艺（大方漆器）', glyph='黔', level='国家级', category='彝族漆器', region='贵州省毕节市大方县', origin='贵州大方',
         abstract='大方漆器为彝族漆器在贵州的一支，皮木胎髹漆彩绘，器壁薄而坚牢，曾进贡宫廷，有「大方漆器，走遍天下」之说。',
         years=44, desc='皮木胎髹涂彩绘皆精，漆器经久耐用，纹样具有黔西北彝族特色。',
         steps='制胎（木/皮）｜髹底漆｜彩绘纹样｜罩漆打磨',
         works='大方漆器碗具｜皮胎彩绘食盒｜描漆屏风小件',
         courses='',
         status='approved', submit_time='2026-09-02 12:50', review_comment='', owner_username='heritage20'),
    dict(name='漆器髹饰技艺（鄱阳脱胎漆器髹饰技艺）', glyph='鄱', level='国家级', category='脱胎漆器', region='江西省上饶市鄱阳县', origin='江西鄱阳',
         abstract='鄱阳脱胎漆器以漆裱布成胎，脱胎后胎体薄如纸、坚如瓷，髹漆推光，曾与景德镇瓷器并称于市。',
         years=35, desc='脱胎胎薄如纸、坚如瓷，髹饰素雅；兼研菠萝漆起纹。',
         steps='裱布夹纻｜脱胎｜髹漆打磨｜推光揩清',
         works='脱胎素面茶盏｜脱胎果盘｜漆布脱胎花瓶',
         courses='',
         status='approved', submit_time='2026-09-02 13:00', review_comment='', owner_username='heritage21'),
    dict(name='婺源菠萝漆器制作技艺', glyph='菠', level='省级', category='犀皮漆', region='江西省上饶市婺源县', origin='江西婺源',
         abstract='婺源菠萝漆以髹涂多色漆与打捻起纹为要，磨显后纹如菠萝斑、行云流转，多用于茶器文具。',
         years=28, desc='菠萝漆打捻起纹手法独到，成品斑纹流动、光润悦目。',
         steps='制胎｜打捻｜层髹色漆｜磨显｜揩清',
         works='菠萝漆笔筒｜云纹茶盏｜斑纹砚盒',
         courses='',
         status='pending', submit_time='2026-09-02 13:10', review_comment='', owner_username='heritage21'),
    dict(name='雕漆技艺（天水雕漆技艺）', glyph='陇', level='国家级', category='雕漆', region='甘肃省天水市秦州区', origin='甘肃天水',
         abstract='天水雕漆在传统雕漆基础上融合雕填、石刻镶嵌与彩绘，器形宏阔、图样繁丽，擅作屏风、箱柜等大件。',
         years=48, desc='以雕填、石刻镶嵌与彩绘见长，所作大屏巨匣构图饱满、工艺繁复。',
         steps='髹漆制胎｜设计图稿｜剔刻/雕填｜嵌石｜打磨揩清',
         works='雕漆青绿山水挂屏｜雕填大漆箱｜嵌石屏风',
         courses='',
         status='approved', submit_time='2026-09-02 13:20', review_comment='', owner_username='heritage22'),
    dict(name='凤翔罩金漆器制作技艺', glyph='罩', level='省级', category='罩金漆器', region='陕西省宝鸡市凤翔区', origin='陕西凤翔',
         abstract='凤翔罩金漆器以金箔罩于漆面之内、久用愈亮为特色，多作屏风、箱柜、插屏，为关中西府传统漆艺。',
         years=31, desc='金箔封于漆里、日久愈亮，屏柜插屏为长，髹漆匀净。',
         steps='制胎｜髹漆底｜贴金箔｜罩漆护金｜打磨',
         works='罩金漆插屏｜金漆柜门饰板｜罩金妆匣',
         courses='',
         status='approved', submit_time='2026-09-02 13:30', review_comment='', owner_username='heritage01'),
    dict(name='雕填漆器髹饰技艺', glyph='填', level='省级', category='雕填', region='河北省廊坊市广阳区', origin='河北廊坊',
         abstract='雕填即先髹漆、后剔刻凹纹、再填色漆磨平，承宫廷造办处漆作一脉；廊坊雕填器身纹彩沉入漆面、光润平整。',
         years=36, desc='雕填、脱胎、金漆镶嵌皆承京作一脉，刻纹填彩工整细致。',
         steps='髹漆制胎｜剔刻纹样｜填彩漆｜磨显｜推光',
         works='雕填花卉提盒｜刻纹填彩盘｜雕填漆器文具',
         courses='雕填漆器 · 刻纹填彩入门',
         status='approved', submit_time='2026-09-02 13:40', review_comment='', owner_username='heritage01'),
    dict(name='脱胎漆器髹饰技艺', glyph='津', level='省级', category='脱胎漆器', region='河北省廊坊市广阳区', origin='河北廊坊',
         abstract='廊坊脱胎漆器以漆裱布成胎、脱模成形，胎体轻坚，多制日用器皿与陈设，属京作漆器南传之地。',
         years=29, desc='以漆布脱胎制日用漆器，师承廊坊京作一脉，胎壁均匀、髹饰素雅。',
         steps='裱布夹纻｜脱胎｜髹漆｜打磨推光',
         works='脱胎素漆茶盘｜夹纻果盒｜脱胎花瓶',
         courses='',
         status='approved', submit_time='2026-09-02 13:50', review_comment='', owner_username='heritage01'),
    dict(name='漆器髹饰技艺（潍坊嵌银髹漆技艺）', glyph='银', level='国家级', category='嵌银髹漆', region='山东省潍坊市', origin='山东潍坊',
         abstract='潍坊嵌银髹漆以银丝嵌入木胎、再髹漆罩护为特色，多作文具箱盒，银线走丝、漆木相映。',
         years=33, desc='银丝入木、髹漆相守，盘匣笔筒为长，走线流畅匀净。',
         steps='木胎开槽｜嵌银丝｜髹漆罩护｜打磨推光',
         works='嵌银髹漆紫檀笔筒｜银丝纹文具匣｜嵌银镇纸',
         courses='',
         status='approved', submit_time='2026-09-02 14:00', review_comment='', owner_username='heritage01'),
    dict(name='桂林漆器制作技艺', glyph='桂', level='省级', category='天然胎漆器', region='广西壮族自治区桂林市', origin='广西桂林',
         abstract='桂林漆器善借竹根、柚壳、葫芦等天然形态制胎髹漆，所谓「以象制器」，随形施髹、巧拙天成。',
         years=30, desc='以竹根、柚壳、葫芦等天然胎髹漆，随形施艺，天然成趣。',
         steps='选天然胎｜去脂打磨｜髹漆打底｜随形髹饰｜推光',
         works='柚壳漆碗｜竹根漆笔洗｜葫芦漆茶罐',
         courses='',
         status='approved', submit_time='2026-09-02 14:10', review_comment='', owner_username='heritage01'),
    dict(name='上海漆器制作技艺', glyph='沪', level='市级', category='平磨螺钿', region='上海市闵行区', origin='上海',
         abstract='上海漆器制作技艺承江南髹饰传统，长于平磨螺钿与雕漆嵌玉，器风精细雅致，多作屏风、陈设与日用漆器。',
         years=35, desc='兼长平磨螺钿与雕漆嵌玉，磨工精细，漆面平整如镜。',
         steps='制胎｜髹漆打底｜螺钿镶嵌｜罩漆｜平磨推光',
         works='平磨螺钿白玉兰赏盘｜嵌玉漆屏｜螺钿文具盒',
         courses='',
         status='approved', submit_time='2026-09-02 14:20', review_comment='', owner_username='heritage01'),
    dict(name='漆器髹饰技艺（阳江漆器髹饰技艺）', glyph='粤', level='国家级', category='髹漆装饰', region='广东省阳江市', origin='广东阳江',
         abstract='阳江漆器以研制腰果漆髹涂见长，漆膜坚韧、耐潮耐热，多作日用漆器与漆画，曾远销南洋。',
         years=39, desc='以腰果漆髹涂日用漆器，薄涂多道、耐潮耐热，光泽内敛耐用。',
         steps='制胎（木/皮/纸）｜髹涂腰果漆｜打磨｜推光',
         works='腰果漆提梁食盒｜漆器漆画屏｜日用漆果盘',
         courses='阳江漆器 · 腰果漆髹涂班',
         status='approved', submit_time='2026-09-02 14:30', review_comment='', owner_username='heritage01'),
    dict(name='金漆画（普宁铁笔金漆画）', glyph='金', level='省级', category='金漆画', region='广东省揭阳市普宁市', origin='广东普宁',
         abstract='普宁铁笔金漆画以铁笔在黑漆推光板上勾金描线，线如发丝、金彩夺目，多施于神龛、屏风与漆器。',
         years=27, desc='铁笔描金走线遒劲，黑漆金画相映生辉，长于神龛屏风装饰。',
         steps='髹黑漆推光｜铁笔勾线｜描金上彩｜罩护',
         works='铁笔金漆画屏风｜金漆画神龛饰板｜描金漆盒',
         courses='',
         status='approved', submit_time='2026-09-02 14:40', review_comment='', owner_username='heritage01'),
    dict(name='傣族漆器制作技艺', glyph='傣', level='省级', category='髹漆彩绘', region='云南省临沧市耿马县', origin='云南耿马（傣族）',
         abstract='傣族漆器以竹篾编胎或木胎髹漆，红黑为底、金漆勾绘龙凤花卉，多用于赕佛与日常盛器，极富民族色彩。',
         years=29, desc='竹篾编胎髹漆彩绘，红黑金三色龙凤纹，器身饱满光润。',
         steps='编胎/制胎｜髹漆打底｜彩绘纹样｜罩漆',
         works='傣式漆器供盘｜彩绘漆奁｜竹胎漆提盒',
         courses='',
         status='approved', submit_time='2026-09-02 14:50', review_comment='', owner_username='heritage01'),
    dict(name='漆刻（昭通漆刻）', glyph='刻', level='省级', category='漆刻', region='云南省昭通市', origin='云南昭通',
         abstract='昭通漆刻以刀在髹好的漆面上剔刻出花鸟人物，再填彩晕染，刻线如画、色彩明快，是云南传统美术。',
         years=33, desc='漆面剔刻填彩，花鸟人物栩栩如生，刀法爽利、色彩明快。',
         steps='髹漆成面｜起稿｜剔刻｜填彩晕染｜罩漆',
         works='漆刻花鸟挂屏｜刻漆人物盘｜漆刻文具盒',
         courses='',
         status='approved', submit_time='2026-09-02 15:00', review_comment='', owner_username='heritage01'),
    dict(name='金漆镶嵌工艺', glyph='桦', level='省级', category='金漆镶嵌', region='黑龙江省哈尔滨市', origin='黑龙江哈尔滨',
         abstract='黑龙江金漆镶嵌工艺承京作金漆镶嵌一脉而自成面貌，多作屏风陈设与日用漆器，镶嵌髹饰并重。',
         years=31, desc='承京作金漆镶嵌一脉，将北地冰雪意象融入镶嵌髹饰，新作求变。',
         steps='制胎｜髹底漆｜镶嵌｜罩漆磨显',
         works='冰雪题材镶嵌漆屏｜金漆镶嵌茶盒｜嵌饰挂屏',
         courses='',
         status='approved', submit_time='2026-09-02 15:10', review_comment='', owner_username='heritage01'),
    dict(name='大漆镶嵌髹饰技艺', glyph='北', level='省级', category='大漆镶嵌', region='黑龙江省', origin='黑龙江',
         abstract='大漆镶嵌髹饰技艺以天然大漆髹涂为地、嵌以螺钿骨石等材料，髹嵌结合，纹饰雅致。',
         years=29, desc='髹涂为地、嵌饰成纹，作品温润耐品。',
         steps='髹漆制胎｜嵌料设计｜镶嵌｜罩漆打磨',
         works='大漆镶嵌茶盘｜嵌螺钿挂件｜漆嵌文具',
         courses='',
         status='pending', submit_time='2026-09-02 15:20', review_comment='', owner_username='heritage33'),
    dict(name='野王纻器制作技艺', glyph='纻', level='省级', category='夹纻纻器', region='河南省焦作市沁阳市', origin='河南沁阳（野王）',
         abstract='野王纻器以麻布漆灰层层夹纻制成器胎，为脱胎漆器之先声，古称「纻器」，器轻而坚，可历久不坏。',
         years=35, desc='麻布漆灰层层夹纻，纻器轻坚耐用，悉遵古法。',
         steps='制模｜裱布夹纻｜刮灰｜髹漆｜脱模修整',
         works='纻器漆盒｜夹纻香盘｜麻布胎茶托',
         courses='',
         status='approved', submit_time='2026-09-02 15:30', review_comment='', owner_username='heritage01'),
]

PRODUCTS = [
    dict(glyph='盏', name='犀皮描金茶盏', craft='犀皮', category='茶器', material='天然生漆 · 脱胎胎体',
         size='口径 8.5cm · 高 6cm', inheritor='张守一', level='国家级', saleable=True, price=368,
         cost_price=120, stock=18, alert_threshold=5, cover='/imgs/product/p00.jpg', images=['/imgs/product/p00.jpg'],
         story='此盏以犀皮打捻技法起纹，多层髹涂后打磨显现流云斑纹，口沿再以描金勾边。一盏一纹，无有雷同。',
         highlights=['犀皮打捻起纹，纹路天然流动', '多层髹涂，历时四十余日', '口沿描金，金漆与犀皮相映', '脱胎工艺，胎薄而坚'],
         status='approved', flag='热销', submit_time='2026-08-20 10:15', review_comment='', owner_username='heritage01'),
    dict(glyph='盘', name='雕漆云纹果盘', craft='雕漆', category='日用', material='天然大漆 · 木胎 · 朱砂入漆',
         size='直径 24cm · 高 4cm', inheritor='赵雕', level='国家级', saleable=True, price=588,
         cost_price=200, stock=7, alert_threshold=5, cover='/imgs/product/p01.jpg', images=['/imgs/product/p01.jpg'],
         story='雕漆一道，刀行漆上。此盘髹朱漆百余道，再以刀剔出云纹，刀法圆熟、纹样流畅。',
         highlights=['朱漆累积百余道', '剔刻云纹，刀法圆熟', '纹样流畅刚柔并济', '朱砂入漆，色泽沉稳'],
         status='approved', flag='', submit_time='2026-08-20 09:40', review_comment='', owner_username='heritage02'),
    dict(glyph='碗', name='剔犀云纹茶碗', craft='剔犀', category='茶器', material='天然大漆 · 木胎',
         size='口径 10cm · 高 6cm', inheritor='赵雕', level='国家级', saleable=False, price=0,
         cost_price=150, stock=5, alert_threshold=3, cover='/imgs/product/p02.jpg', images=['/imgs/product/p02.jpg'],
         story='剔犀而成的云纹茶碗，多层漆色交叠，刀口处现出含蓄的层次之美，是一种低调的奢华。',
         highlights=['剔犀多层髹涂', '云纹刀法利落', '低调内敛之美'],
         status='approved', flag='', submit_time='2026-08-20 09:50', review_comment='', owner_username='heritage02'),
    dict(glyph='盒', name='螺钿首饰盒', craft='螺钿', category='日用', material='螺钿 · 木胎 · 软锦内衬',
         size='长 15cm · 宽 10cm · 高 8cm', inheritor='钱螺', level='省级', saleable=True, price=688,
         cost_price=260, stock=12, alert_threshold=5, cover='/imgs/product/p03.jpg', images=['/imgs/product/p03.jpg'],
         story='贝华镶盒，外饰螺钿缠枝，内衬软锦。收纳钗环首饰，开合之间，光华内敛。',
         highlights=['螺钿贝华镶嵌', '软锦内衬护物', '缠枝纹样华美'],
         status='pending', flag='', submit_time='2026-09-01 15:30', review_comment='', owner_username='heritage01'),
    dict(glyph='屏', name='款彩山水挂屏', craft='款彩', category='摆件', material='色漆 · 灰 · 木胎',
         size='高 50cm · 宽 36cm', inheritor='张守一', level='国家级', saleable=False, price=0,
         cost_price=400, stock=2, alert_threshold=2, cover='/imgs/product/p04.jpg', images=['/imgs/product/p04.jpg'],
         story='款彩一道，刻灰填彩。此屏以刀刻出山水纹样，再填以浓烈色彩，刀法爽利、色采浓烈。',
         highlights=['刻灰填彩', '刀法爽利', '山水题材气势磅礴'],
         status='rejected', flag='', submit_time='2026-08-29 11:00', review_comment='作品故事描述过于简单，请补充创作理念与工艺细节；另请附多角度照片。', owner_username='heritage01'),
    dict(glyph='匣', name='推光漆 · 描金缠枝首饰匣', craft='推光漆', category='日用', material='天然大漆 · 实木胎',
         size='长 20cm · 宽 13cm · 高 9cm', inheritor='郑寿山', level='国家级', saleable=True, price=980,
         cost_price=360, stock=9, alert_threshold=3, cover='/imgs/product/p05.jpg', images=['/imgs/product/p05.jpg'],
         story='平遥推光为骨，描金缠枝为饰。掌推光出的漆面平滑如镜，开合之间流光可鉴。',
         highlights=['手掌推光，漆面如镜', '描金缠枝纹细腻', '天然大漆髹涂二十余道'],
         status='approved', flag='', submit_time='2026-09-03 11:00', review_comment='', owner_username='heritage04'),
    dict(glyph='杯', name='脱胎漆器 · 蝉纹主人杯', craft='脱胎漆器', category='茶器', material='天然大漆 · 夏布夹纻',
         size='口径 7.5cm · 高 6cm', inheritor='梁福宁', level='国家级', saleable=True, price=1280,
         cost_price=460, stock=6, alert_threshold=3, cover='/imgs/product/p06.jpg', images=['/imgs/product/p06.jpg'],
         story='夏布夹纻脱胎而成，胎薄而坚、轻若蝉翼，杯身髹以蝉纹，莹润素雅。',
         highlights=['夹纻脱胎，质轻而坚', '蝉纹髹绘清雅', '手作小批，每只略有差异'],
         status='approved', flag='新品', submit_time='2026-09-03 11:10', review_comment='', owner_username='heritage09'),
    dict(glyph='瓶', name='脱胎漆器 · 福寿寿桃摆瓶', craft='脱胎漆器', category='摆件', material='天然大漆 · 夹纻',
         size='高 32cm', inheritor='梁福宁', level='国家级', saleable=True, price=2680,
         cost_price=1100, stock=4, alert_threshold=2, cover='/imgs/product/p07.jpg', images=['/imgs/product/p07.jpg'],
         story='寿桃造型夹纻脱胎，通体朱漆髹饰，摆于案头寓意福寿绵长。',
         highlights=['脱胎成形，轻盈坚固', '朱漆髹饰温润'],
         status='pending', flag='', submit_time='2026-09-03 11:15', review_comment='', owner_username='heritage09'),
    dict(glyph='台', name='点螺 · 千里江山茶台', craft='点螺', category='茶器', material='天然大漆 · 点螺贝片',
         size='长 36cm · 宽 20cm', inheritor='沈砚秋', level='国家级', saleable=True, price=3280,
         cost_price=1400, stock=3, alert_threshold=2, cover='/imgs/product/p08.jpg', images=['/imgs/product/p08.jpg'],
         story='以点螺之法将薄贝片点嵌成千里江山，山色随光流转，是案上的一幅「贝上丹青」。',
         highlights=['点螺薄贝，随光变幻', '千里江山构图', '工细数月的慢手艺'],
         status='approved', flag='精品', submit_time='2026-09-03 11:20', review_comment='', owner_username='heritage07'),
    dict(glyph='杯', name='犀皮漆 · 云纹主人杯', craft='犀皮漆', category='茶器', material='天然大漆 · 木胎',
         size='口径 7cm · 高 5.5cm', inheritor='甘玉成', level='国家级', saleable=True, price=1280,
         cost_price=430, stock=8, alert_threshold=3, cover='/imgs/product/p09.jpg', images=['/imgs/product/p09.jpg'],
         story='打埝起纹后髹以多色漆，磨显出的流动纹理每道皆不重复，天然自成。',
         highlights=['犀皮打埝，纹理天然', '多色髹涂显花', '一盏一纹不可复制'],
         status='approved', flag='热销', submit_time='2026-09-03 11:25', review_comment='', owner_username='heritage15'),
    dict(glyph='奁', name='楚式漆器 · 凤鸟纹圆奁盒', craft='髹漆彩绘', category='日用', material='天然大漆 · 木胎',
         size='直径 18cm · 高 10cm', inheritor='邹槐安', level='国家级', saleable=True, price=1580,
         cost_price=560, stock=5, alert_threshold=2, cover='/imgs/product/p10.jpg', images=['/imgs/product/p10.jpg'],
         story='髹朱黑二漆，朱髹底、黑髹盖，彩绘凤鸟卷云纹，楚风宛然。',
         highlights=['朱黑髹饰，楚韵十足', '凤鸟卷云纹彩绘', '实用收纳两相宜'],
         status='approved', flag='', submit_time='2026-09-03 11:30', review_comment='', owner_username='heritage16'),
    dict(glyph='盘', name='软螺钿 · 缠枝莲纹盘', craft='螺钿', category='日用', material='软螺钿贝片 · 大漆',
         size='直径 20cm', inheritor='李爱华', level='国家级', saleable=True, price=880,
         cost_price=300, stock=10, alert_threshold=3, cover='/imgs/product/p11.jpg', images=['/imgs/product/p11.jpg'],
         story='贝片薄如蝉翼，嵌出缠枝莲纹，通体罩透明漆，光华流转不刺目。',
         highlights=['软螺钿薄贝镶嵌', '缠枝莲纹典雅', '罩漆后温润耐看'],
         status='approved', flag='', submit_time='2026-09-03 11:35', review_comment='', owner_username='heritage06'),
    dict(glyph='壶', name='剔犀 · 如意云纹执壶', craft='剔犀', category='茶器', material='天然大漆 · 铜木内胎',
         size='高 14cm', inheritor='卫子谦', level='国家级', saleable=True, price=1680,
         cost_price=620, stock=3, alert_threshold=2, cover='/imgs/product/p12.jpg', images=['/imgs/product/p12.jpg'],
         story='剔犀云雕，刀口现出朱黑相间的层色，如行云流水，光素里藏着功夫。',
         highlights=['绛州剔犀，层色分明', '如意云纹流转', '刀法利落含蓄'],
         status='approved', flag='', submit_time='2026-09-03 11:40', review_comment='', owner_username='heritage05'),
    dict(glyph='筒', name='嵌银髹漆 · 紫檀笔筒', craft='嵌银髹漆', category='文房', material='紫檀 · 银丝 · 大漆',
         size='口径 10cm · 高 12cm', inheritor='于春华', level='国家级', saleable=True, price=1180,
         cost_price=420, stock=7, alert_threshold=3, cover='/imgs/product/p13.jpg', images=['/imgs/product/p13.jpg'],
         story='银丝走线嵌出缠枝纹，髹漆罩护，木纹、银线与漆光相映成趣。',
         highlights=['银丝嵌线精细', '紫檀木胎温润', '髹漆护木久用愈亮'],
         status='approved', flag='', submit_time='2026-09-03 11:45', review_comment='', owner_username='heritage26'),
    dict(glyph='屏', name='雕漆 · 青绿山水挂屏', craft='雕漆', category='摆件', material='天然大漆 · 木胎 · 矿物色',
         size='高 55cm · 宽 38cm', inheritor='张铁山', level='国家级', saleable=True, price=3280,
         cost_price=1500, stock=2, alert_threshold=1, cover='/imgs/product/p14.jpg', images=['/imgs/product/p14.jpg'],
         story='髹漆数十道后剔刻山石树木，青绿设色取自天然矿物，一幅漆上山水。',
         highlights=['髹漆剔刻，层次深厚', '青绿矿物设色', '陇上漆艺之大件'],
         status='approved', flag='', submit_time='2026-09-03 11:50', review_comment='', owner_username='heritage22'),
    dict(glyph='盒', name='阳江漆器 · 提梁食盒', craft='髹漆', category='日用', material='皮纸胎 · 腰果漆',
         size='三层 · 高 26cm', inheritor='尹治平', level='国家级', saleable=True, price=680,
         cost_price=240, stock=14, alert_threshold=4, cover='/imgs/product/p15.jpg', images=['/imgs/product/p15.jpg'],
         story='皮纸制胎、腰果漆髹涂，耐潮耐热，提梁食盒是阳江人走亲访友的体面家什。',
         highlights=['腰果漆耐潮耐用', '皮纸胎轻便坚固', '日用器物不失体面'],
         status='approved', flag='', submit_time='2026-09-03 11:55', review_comment='', owner_username='heritage29'),
    dict(glyph='屏', name='金漆镶嵌 · 百宝嵌插屏', craft='金漆镶嵌', category='摆件', material='大漆 · 玉石贝壳 · 金箔',
         size='高 30cm · 宽 22cm', inheritor='姚镜春', level='国家级', saleable=False, price=0,
         cost_price=2600, stock=2, alert_threshold=1, cover='/imgs/product/p16.jpg', images=['/imgs/product/p16.jpg'],
         story='以玉石、螺钿、金银片嵌出花果图，宝色璀璨，京作金漆镶嵌的集大成小品。',
         highlights=['百宝镶嵌，宝色流光', '京作金漆镶嵌一脉'],
         status='pending', flag='', submit_time='2026-09-03 12:00', review_comment='', owner_username='heritage03'),
    dict(glyph='像', name='干漆夹苎 · 水月观音', craft='夹苎脱胎', category='造像', material='漆 · 苎麻 · 金箔',
         size='高 45cm', inheritor='童启山', level='国家级', saleable=False, price=0,
         cost_price=5000, stock=1, alert_threshold=1, cover='/imgs/product/p17.jpg', images=['/imgs/product/p17.jpg'],
         story='以干漆夹苎法塑水月观音，历时数月髹饰贴金，法相庄严，为馆藏级非卖造像。',
         highlights=['干漆夹苎，历千年不朽', '髹漆贴金，庄严肃穆', '非卖馆藏，只作展示'],
         status='approved', flag='镇馆', submit_time='2026-09-03 12:05', review_comment='', owner_username='heritage12'),
]

PRODUCT_STOCK_RECORDS = [
    dict(product_name='犀皮描金茶盏', type='in', qty=20, note='初仓入库', operator='平台管理员', time='2026-08-20 10:00'),
    dict(product_name='雕漆云纹果盘', type='in', qty=8, note='初仓入库', operator='平台管理员', time='2026-08-20 10:05'),
    dict(product_name='剔犀云纹茶碗', type='in', qty=5, note='初仓入库', operator='平台管理员', time='2026-08-20 10:10'),
    dict(product_name='犀皮描金茶盏', type='order', qty=2, note='订单销售出库', operator='平台管理员', time='2026-08-31 20:15'),
    dict(product_name='雕漆云纹果盘', type='order', qty=1, note='订单销售出库', operator='平台管理员', time='2026-08-29 18:20'),
    dict(product_name='推光漆 · 描金缠枝首饰匣', type='in', qty=10, note='初仓入库', operator='平台管理员', time='2026-09-03 12:10'),
    dict(product_name='推光漆 · 描金缠枝首饰匣', type='order', qty=1, note='订单销售出库', operator='平台管理员', time='2026-09-03 12:30'),
    dict(product_name='脱胎漆器 · 蝉纹主人杯', type='in', qty=7, note='初仓入库', operator='平台管理员', time='2026-09-03 12:15'),
    dict(product_name='脱胎漆器 · 蝉纹主人杯', type='order', qty=1, note='订单销售出库', operator='平台管理员', time='2026-09-03 12:40'),
    dict(product_name='点螺 · 千里江山茶台', type='in', qty=3, note='初仓入库', operator='平台管理员', time='2026-09-03 12:20'),
    dict(product_name='犀皮漆 · 云纹主人杯', type='in', qty=8, note='初仓入库', operator='平台管理员', time='2026-09-03 12:25'),
    dict(product_name='楚式漆器 · 凤鸟纹圆奁盒', type='in', qty=5, note='初仓入库', operator='平台管理员', time='2026-09-03 12:30'),
    dict(product_name='软螺钿 · 缠枝莲纹盘', type='in', qty=10, note='初仓入库', operator='平台管理员', time='2026-09-03 12:35'),
    dict(product_name='剔犀 · 如意云纹执壶', type='in', qty=3, note='初仓入库', operator='平台管理员', time='2026-09-03 12:40'),
    dict(product_name='嵌银髹漆 · 紫檀笔筒', type='in', qty=7, note='初仓入库', operator='平台管理员', time='2026-09-03 12:45'),
    dict(product_name='雕漆 · 青绿山水挂屏', type='in', qty=2, note='初仓入库', operator='平台管理员', time='2026-09-03 12:50'),
    dict(product_name='阳江漆器 · 提梁食盒', type='in', qty=14, note='初仓入库', operator='平台管理员', time='2026-09-03 12:55'),
    dict(product_name='犀皮漆 · 云纹主人杯', type='order', qty=1, note='订单销售出库', operator='平台管理员', time='2026-09-03 13:00'),
    dict(product_name='软螺钿 · 缠枝莲纹盘', type='out', qty=1, note='损耗/次品隔离', operator='平台管理员', time='2026-09-03 13:05'),
]

TRAINING_RECORDS = [
    dict(course_name='半日髹漆体验 · 素色茶碗', teacher='张守一',
         content='认识生漆与常用工具，讲解制胎-裱布-刮灰-髹涂的完整流程，学员完成首道髹涂实操。',
         attendance=[{'name': '余老板', 'status': 'present'}, {'name': '杨柳', 'status': 'present'}],
         assessment={'余老板': '优秀，手法稳，可进阶系统课', '杨柳': '良好，需多练阴干控制'}, remark='课堂照片已归档'),
    dict(course_name='髹漆系统课程 · 基础班', teacher='张守一',
         content='讲解打底与裱布刮灰要点，示范多道髹涂与阴干控制，学员跟练裱布。',
         attendance=[{'name': '陈秋白', 'status': 'present'}, {'name': '周小雅', 'status': 'present'},
                     {'name': '赵一鸣', 'status': 'present'}],
         assessment={'陈秋白': '优秀', '周小雅': '良好', '赵一鸣': '良好，上手快'}, remark=''),
    dict(course_name='髹漆系统课程 · 基础班', teacher='张守一',
         content='演示中涂水磨找平与精修口沿，讲解各段阴干的温湿度把控。',
         attendance=[{'name': '陈秋白', 'status': 'present'}, {'name': '周小雅', 'status': 'absent'},
                     {'name': '赵一鸣', 'status': 'present'}],
         assessment={'陈秋白': '优秀，打磨细致'}, remark='周小雅请假，已约补课'),
    dict(course_name='半日髹漆体验 · 素色茶碗', teacher='张守一',
         content='第二场体验课堂：示范裱布与刮灰后的首道髹涂，指导学员控制刷漆厚薄与阴干。',
         attendance=[{'name': '徐伯安', 'status': 'present'}, {'name': '高启铭', 'status': 'present'}],
         assessment={'徐伯安': '良好，髹涂均匀', '高启铭': '优秀，已续报系统课'}, remark=''),
    dict(course_name='雕漆系统课程 · 刀法班', teacher='赵雕',
         content='识刀磨刀入门：讲解各型号刻刀与开刃保养，学员跟练执刀与运刀基础。',
         attendance=[{'name': '何文远', 'status': 'present'}, {'name': '孙雪', 'status': 'present'},
                     {'name': '方奕', 'status': 'absent'}],
         assessment={'何文远': '良好，腕力控制佳', '孙雪': '良好', '方奕': '请假，安排补课'}, remark='刀法班开课首场'),
]

def build_lessons(items, video_url=''):
    out = []
    for i, (title, desc) in enumerate(items, 1):
        lesson = {
            'num': str(i), 'title': title, 'desc': desc,
            'video': '', 'videoName': '', 'videoStatus': 'draft',
            'videoReviewComment': '', 'scheduleDate': '', 'scheduleTime': '',
        }
        if i == 1 and video_url:
            lesson.update({'video': video_url, 'videoName': f'{title}.mp4', 'videoStatus': 'approved'})
        out.append(lesson)
    return out


HALF_DAY_LESSONS = [
    ('认识生漆与常用工具', '从漆树的采割讲起，认识生漆的特性与保存方法；演示制胎、打底的基础动作并跟练。'),
    ('亲手髹涂 · 素色茶碗', '指导学员完成裱布、刮灰后的首道髹涂，讲解阴干要领，作品完成后可带走。'),
]
BASIC_LESSONS = [
    ('大漆基本功 · 工具与安全', '认识各类髹涂工具，讲解通风与漆酚过敏防护，演示调漆与漆面判断。'),
    ('木胎选料与预处理', '认识常见胎体木料，练习去脂、粗磨、除尘等预处理工序。'),
    ('裱布：让胎体更牢固', '讲解裱布走刀与刷漆手法，实操为茶碗/盘胎裱布。'),
    ('刮灰：底灰的配比与找平', '配比瓦灰与生漆调制底灰，练习刮灰找平。'),
    ('第一道髹涂', '以稀漆渗灰上底漆，掌握薄而匀的髹涂手法。'),
    ('色漆的调制', '研磨色料与生漆调漆，观察漆色在不同光下的变化。'),
    ('多层髹涂与阴干节奏', '控制每道厚薄与阴干温湿度，体会「漆要养」的节奏。'),
    ('中涂打磨', '水磨中涂，找平细面，为面漆做准备。'),
    ('推光前的最后修整', '精修口沿与底面，清理砂痕与流漆。'),
    ('推光 · 让漆面透亮', '依次细磨、揩清、推光，练出镜面般的漆面。'),
    ('揩清与日常保养', '完成揩清工序，学习漆器日后的使用与保养要点。'),
    ('结课创作 · 独立完成一件素器', '综合运用全流程，独立完成并带走一件素色髹漆器物。'),
]
DIAOQI_LESSONS = [
    ('识刀与磨刀', '认识剔犀/剔红各类刻刀型号，练习磨刀开刃与保养。'),
    ('执刀与运刀手法', '练习刀距、入漆角度与运刀节奏，体会「刀随腕走」。'),
    ('云纹起稿与构图', '拓印云纹稿、布图定位，设计自己的纹样。'),
    ('剔漆基础功', '在素面漆层上试剔，练深度均匀与走刀利落。'),
    ('剔犀 · 层色显现', '剔开多层色漆，让云纹层次逐层显现。'),
    ('剔红 · 花卉纹样', '完成一件剔红花卉纹样小样。'),
    ('修光与打磨', '修整刀口毛边，打磨漆面至平滑。'),
    ('独立成器 · 剔犀果盘', '综合运用刀法，完成一只剔犀云纹果盘的剔刻。'),
]
LUODIAN_LESSONS = [
    ('认识螺钿与贝材', '认识不同贝片的光泽与质感，练习裁切与打磨贝片。'),
    ('镶嵌设计与粘贴', '按纹样划线布局，练习平贴镶嵌。'),
    ('打磨找平', '将镶嵌面磨平，使贝片与漆面齐整。'),
    ('罩漆与揩清', '罩透明漆阴干，揩清推光，完成作品。'),
]
MIAOJIN_LESSONS = [
    ('金漆的种类与调配', '认识泥金、箔金与金漆的区别，学习调金漆。'),
    ('笔法基础 · 描线', '练中锋勾线与钉头鼠尾，掌握粗细变化。'),
    ('纹样设计 · 缠枝', '临摹缠枝莲纹，独立起小稿。'),
    ('勾金打底', '以淡金勾出纹样底稿。'),
    ('上金与晕染', '练习上金厚薄与晕染过渡。'),
    ('罩漆收尾 · 装裱成幅', '罩漆阴干，完成一幅描金小品。'),
]
PINGYAO_LESSONS = [
    ('认识平遥推光漆', '平遥以天然大漆髹涂与推光见长；认识推光漆用料与工具。'),
    ('打底 · 裱布 · 刮灰', '木胎打底、裱布刮灰，打磨找平出光洁漆地。'),
    ('掌推光 · 细砖灰研磨', '以手掌蘸细砖灰与发团循序研磨漆面，练推光手法。'),
    ('揩清成镜 · 保养', '揩清揩光，让漆面呈镜般光润，学习日常保养。'),
]
TUOTAI_LESSONS = [
    ('认识脱胎与夏布', '脱胎以漆裱布成型、质轻而坚；认识夏布与大漆夹纻原理。'),
    ('裱布夹纻', '在胎模上逐层裱布、髹漆，累积出胎壳厚度。'),
    ('脱模修整', '胎壳干透后脱去胎模，修整口沿与内外壁。'),
    ('髹漆推光收尾', '内壁髹涂、外壁打磨推光，完成脱胎小盏。'),
]
PIXI_LESSONS = [
    ('认识犀皮（菠萝漆）', '徽州犀皮以多色漆打埝起纹、磨显成花；认识色漆层与埝。'),
    ('打埝 · 起纹', '以稠漆在胎面堆出高低埝纹，控制埝形走向。'),
    ('多层髹涂色漆', '依序髹涂深浅色漆，层叠色带。'),
    ('研磨显纹', '水磨显花，让流畅回旋的犀皮纹理自然浮现。'),
]
CHUSHI_LESSONS = [
    ('楚式漆器与髹饰传统', '认识春秋战国楚式漆器的髹涂与彩绘传统。'),
    ('木胎髹底漆', '制胎后髹朱/黑底漆，打磨出温润漆地。'),
    ('彩绘描漆 · 凤鸟纹', '以毛笔蘸漆彩绘勾描楚风纹样，练习线条与填彩。'),
    ('罩漆揩清', '罩透明漆、揩清收尾，完成一件楚风漆盘。'),
]
YANGJIANG_LESSONS = [
    ('认识阳江漆器与腰果漆', '阳江漆器以研制的腰果漆见长；认识其特性与髹涂差别。'),
    ('制胎髹涂', '在木/皮/纸胎上髹涂腰果漆，多次薄涂阴干。'),
    ('打磨推光', '水磨推光，使日用漆器耐潮耐用、光泽内敛。'),
]
DIATIAN_LESSONS = [
    ('认识雕填工艺', '雕填即刻纹填彩，承宫廷造办处漆作一脉；认识工具与工序。'),
    ('髹漆与雕刻起纹', '漆面髹涂后以刀刻出纹样凹槽。'),
    ('填彩与磨显', '填色漆入凹槽、干后磨平，纹彩沉入漆面。'),
    ('推光收尾', '揩清推光，让雕填纹样与漆面浑然一体。'),
]

TIXI_LESSONS = [
    ('绛州剔犀 · 识刀与磨刀', '认识剔犀各类刻刀型号，练习磨刀开刃与日常保养。'),
    ('云纹起稿 · 布图定位', '临摹绛州云雕经典如意云纹，在漆胎上拓印布图定位。'),
    ('执刀运刀 · 入漆角度', '练习刀距、入漆角度与运刀节奏，体会「刀随腕走」。'),
    ('剔刻层色 · 云纹现彩', '层层剔开黑红黄三色漆，让云纹与层色分明显现。'),
    ('修光打磨', '修整刀口毛边，打磨漆面至温润平滑。'),
    ('成器 · 剔犀云纹镇纸', '综合运用剔刻手法，完成一件剔犀云纹镇纸并学习保养。'),
]
DIANLUO_LESSONS = [
    ('认识点螺与选贝', '点螺以极薄贝片镶拼成画；认识扬州点螺用料与切贝工具。'),
    ('起稿与切贝', '按画稿裁切贝片，拼样定稿。'),
    ('细嵌点入', '将贝片依序点入漆地，完成细密镶嵌。'),
    ('罩漆揩清', '罩透明漆阴干、揩清推光，让贝彩莹然生辉。'),
]
KUANCAI_LESSONS = [
    ('款彩源流 · 灰地打底', '苏州款彩即刻灰填彩；讲解工序源流，示范灰地打底刮灰。'),
    ('画稿上样', '将山水花鸟稿拓印到灰地上。'),
    ('刻灰起线', '以刀依线刻入灰地，剔出凹槽，线条深浅有致。'),
    ('填彩晕色', '将色料填入凹槽并晕染过渡，如着色画稿。'),
    ('磨平固彩', '磨平彩面、罩漆固彩，使纹彩沉入漆地。'),
    ('装裱成幅 · 款彩小挂屏', '完成一件款彩小品并学习装裱成幅。'),
]
QIXIANDIAO_LESSONS = [
    ('认识漆线雕 · 捻线', '漆线雕以捻线盘绕、贴金庄严见长；学习用漆土搓制粗细漆线。'),
    ('盘线起样', '依图样在牌面上盘绕出基础纹样轮廓。'),
    ('堆叠塑形', '以多层漆线堆出浮雕般的起伏与力道。'),
    ('贴金成辉 · 漆线平安牌', '上金箔收尾，完成一块漆线雕平安牌。'),
]
JIAZHU_LESSONS = [
    ('认识干漆夹苎', '天台干漆夹苎以漆麻裱塑佛像闻名；认识「漆麻相合」原理与漆灰配比。'),
    ('捻麻上灰', '练习漆麻捻合与调灰，掌握灰料浓稠。'),
    ('胚体裱塑', '在胎样上逐层裱麻、髹漆，塑出器物形体。'),
    ('阴干加厚', '控制阴干节奏，层层加厚至胎壳坚固。'),
    ('脱模修整', '胎壳干透后脱去胎样，修整口沿与内外壁。'),
    ('髹漆收尾', '髹面漆打磨，完成一件夹苎小器。'),
]
NIJIN_LESSONS = [
    ('认识泥金彩漆', '宁波以朱漆描金为十里红妆髹嫁奁；认识泥金、堆塑用料与工具。'),
    ('木胎髹朱漆', '为器物髹朱红底漆，打磨出温润漆地。'),
    ('堆塑纹样', '以漆灰堆出花鸟纹样的立体起伏。'),
    ('描金收尾', '以金泥勾描纹样，完成一件漆金小品。'),
]
PINGYANG_LESSONS = [
    ('认识平阳漆器', '平阳漆器承宋元温州漆器一脉；认识用料与素髹传统。'),
    ('打底刮灰', '木胎打底、裱布刮灰，打磨找平。'),
    ('宋韵髹涂', '薄涂多遍髹出素净漆面，体会「素髹见真」之美。'),
    ('揩光收尾', '揩清推光，让漆面润泽内敛。'),
]
BAQI_LESSONS = [
    ('走进漆林 · 认识漆树', '利川坝漆以「坝漆清如油，照见美人头」闻名；走进漆林认识漆树与割漆季节。'),
    ('观割漆 · 会滴漆', '观看开刀割漆，观察漆液滴落与漆酚特性。'),
    ('滤漆与晒制', '学习滤渣、晒漆等初制工序，明白生漆来之不易。'),
    ('试髹一器', '以坝漆为一件小木器试髹、阴干，体会生漆本色。'),
]
YANMO_LESSONS = [
    ('认识研磨彩绘', '研磨彩绘以多层彩漆研磨显色见长；认识原料与「磨出来的彩」工序。'),
    ('底胎髹涂与堆漆', '在底胎上髹涂、堆漆出纹样起伏。'),
    ('罩漆层叠', '罩多道色漆与透明漆，层叠出色彩纵深。'),
    ('研磨显彩', '以水磨逐层研磨，让内藏彩纹自然浮现。'),
    ('精磨抛光', '细磨抛光，令漆面如镜、纹理沉静。'),
    ('成器 · 研磨彩绘茶盘', '完成一件研磨彩绘茶盘并学习养护。'),
]
YIZU_LESSONS = [
    ('认识彝族漆器', '彝族漆器黑红黄三色手绘，纹样取自日月山川；认识器型与纹样寓意。'),
    ('起稿 · 三色纹样', '临摹日月、羊角、火镰等经典彝纹。'),
    ('手绘上彩', '以漆笔在黑地上描红黄纹样，一笔成线。'),
    ('成器 · 三色漆碗', '完成一只三色漆碗，学习晾干与保养。'),
]
ZHAOJIN_LESSONS = [
    ('认识罩金漆器', '凤翔罩金将金箔封于漆里、日久愈亮；认识「金在漆里」的工序。'),
    ('髹漆为地', '为器胎髹黑漆打底，打磨出光洁漆面。'),
    ('贴金罩漆', '贴箔后罩透明漆，让金彩沉入漆层。'),
    ('开金看色', '打磨罩面、显现金彩，完成一件罩金小屏牌。'),
]
QIANYIN_LESSONS = [
    ('认识嵌银髹漆', '潍坊嵌银以银丝入木、漆木同心见长；认识工具与银丝备料。'),
    ('设计走线 · 刻槽', '设计吉祥纹样并在木胎上刻出槽线。'),
    ('嵌银入槽', '将银丝敲入槽内、锤平固定。'),
    ('髹漆封固', '髹漆封固银丝与槽口，阴干。'),
    ('磨显抛光', '打磨显露银丝、抛光漆面，银木漆三者同辉。'),
    ('成器 · 嵌银镇尺', '完成一件嵌银髹漆镇尺。'),
]
PINGMO_LESSONS = [
    ('认识平磨螺钿', '上海平磨螺钿以贝片入漆、磨平如画见长；认识贝材与素髹底胎。'),
    ('裁贝拼样', '按稿裁切贝片，拼出花鸟图样。'),
    ('平贴打磨', '平贴贝片后整体水磨，让贝面与漆面齐平。'),
    ('揩清收尾', '揩清推光，完成一件平磨螺钿漆器。'),
]
JINQIHUA_LESSONS = [
    ('认识铁笔金漆画', '普宁金漆画以铁笔在黑漆板上描金刻线见长；认识工具与用料。'),
    ('黑漆板备制', '学习髹黑漆、推光出镜面底板。'),
    ('稿样描印', '将花鸟人物稿印上漆板。'),
    ('铁笔勾线', '以铁笔勾刻金线纹理，落笔如画。'),
    ('金漆填描', '描金填色，让画面在幽暗中熠熠生辉。'),
    ('装框成幅', '完成一件金漆画小品并学习装框。'),
]
DAI_LESSONS = [
    ('认识傣族漆器', '耿马傣家以竹篾编胎、髹漆彩绘见长；认识竹胎与红黑金用色。'),
    ('竹篾编胎', '学习以细竹篾编织器物胎身。'),
    ('髹漆彩绘', '在竹胎上髹黑漆打底，描红金龙凤纹。'),
    ('成器 · 傣家漆碗', '完成一件傣族漆器，了解晾制与防裂要领。'),
]
QIKE_LESSONS = [
    ('认识昭通漆刻', '昭通漆刻以刀在漆面剔刻、填彩晕染见长；认识工具与髹漆底胎。'),
    ('髹漆为底', '在器物上髹涂多层漆地，打磨平顺。'),
    ('画稿刻线', '将花鸟人物稿印上漆面。'),
    ('剔刻去地', '以刀剔刻纹样，留出主形、去地见胎。'),
    ('填彩晕染', '在刻痕中填彩晕色，如画其上。'),
    ('罩漆成器', '罩漆固彩，完成一件漆刻作品。'),
]

COURSES = [
    dict(name='半日髹漆体验 · 素色茶碗', craft='髹漆', stage='体验工作坊', difficulty='零基础', duration='半日',
         schedule='2026-09-20 14:00', capacity=12, price_num=198, cover='/imgs/course/c00.jpg', video=SAMPLE_VIDEO,
         desc='零基础半日课堂，认识生漆，亲手髹制一只素色茶碗，成品带回家。',
         status='approved', submit_time='2026-08-20 09:20', review_comment='',
         lessons=build_lessons(HALF_DAY_LESSONS, SAMPLE_VIDEO), owner_username='heritage01'),
    dict(name='周末螺钿镶嵌体验', craft='螺钿', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-09-27 10:00', capacity=12, price_num=368, cover='/imgs/course/c01.jpg',
         desc='亲手制胎、上漆、推光，做一只大漆主人杯，体验螺钿镶嵌与髹漆之美。',
         status='pending', submit_time='2026-09-01 11:40', review_comment='',
         lessons=build_lessons(LUODIAN_LESSONS), owner_username='heritage01'),
    dict(name='描金漆画进阶工作坊', craft='描金', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-09-26 09:30', capacity=10, price_num=680, cover='/imgs/course/c02.jpg',
         desc='从金漆调配到纹样勾勒，系统学习描金漆画的进阶技法，完成一幅描金小品。',
         status='draft', submit_time='', review_comment='',
         lessons=build_lessons(MIAOJIN_LESSONS), owner_username='heritage01'),
    dict(name='髹漆系统课程 · 基础班', craft='髹漆', stage='系统课程', difficulty='进阶', duration='12 课时',
         schedule='2026-09-13 09:30', capacity=16, price_num=980, cover='/imgs/course/c03.jpg', video=SAMPLE_VIDEO,
         desc='从制胎打底到推光揩清，系统掌握髹漆全流程，独立完成一件器物。',
         status='approved', submit_time='2026-08-20 14:15', review_comment='',
         lessons=build_lessons(BASIC_LESSONS, SAMPLE_VIDEO), owner_username='heritage01'),
    dict(name='雕漆系统课程 · 刀法班', craft='雕漆', stage='系统课程', difficulty='进阶', duration='8 课时',
         schedule='2026-09-19 10:00', capacity=8, price_num=1280, cover='/imgs/course/c04.jpg', video=SAMPLE_VIDEO,
         desc='以刻刀为笔，掌握剔红/剔犀刀法要领，独立完成一件雕漆纹样作品。',
         status='approved', submit_time='2026-08-20 16:00', review_comment='',
         lessons=build_lessons(DIAOQI_LESSONS, SAMPLE_VIDEO), owner_username='heritage02'),
    dict(name='平遥推光漆器 · 掌上推光工作坊', craft='推光漆', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-10-10 10:00', capacity=12, price_num=880, cover='/imgs/course/c05.jpg', video=SAMPLE_VIDEO,
         desc='在平遥传承人指导下，体验裱布刮灰与手掌推光，做一只镜面般的推光漆器小件。',
         status='approved', submit_time='2026-09-03 09:00', review_comment='',
         lessons=build_lessons(PINGYAO_LESSONS, SAMPLE_VIDEO), owner_username='heritage04'),
    dict(name='福州脱胎漆器 · 夹纻制盏班', craft='脱胎漆器', stage='系统课程', difficulty='进阶', duration='12 课时',
         schedule='2026-10-17 09:30', capacity=10, price_num=1180, cover='/imgs/course/c06.jpg', video=SAMPLE_VIDEO,
         desc='从裱布夹纻到脱模修整，亲手做一只质轻而坚的脱胎漆盏，体验「脱胎换骨」。',
         status='approved', submit_time='2026-09-03 09:20', review_comment='',
         lessons=build_lessons(TUOTAI_LESSONS, SAMPLE_VIDEO), owner_username='heritage09'),
    dict(name='徽州犀皮漆 · 打埝磨显班', craft='犀皮漆', stage='系统课程', difficulty='进阶', duration='8 课时',
         schedule='2026-10-24 10:00', capacity=10, price_num=980, cover='/imgs/course/c07.jpg',
         desc='学习打埝起纹与多色髹涂，研磨显花，体会犀皮漆「天然自成」的流动纹理。',
         status='pending', submit_time='2026-09-03 09:40', review_comment='',
         lessons=build_lessons(PIXI_LESSONS), owner_username='heritage15'),
    dict(name='楚风漆器 · 髹绘工作坊', craft='髹漆彩绘', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-10-18 14:00', capacity=12, price_num=760, cover='/imgs/course/c08.jpg',
         desc='在朱黑之间学习楚式髹涂与凤鸟纹彩绘，带走一只楚风漆盘。',
         status='pending', submit_time='2026-09-03 10:00', review_comment='',
         lessons=build_lessons(CHUSHI_LESSONS), owner_username='heritage16'),
    dict(name='雕填漆器 · 刻纹填彩入门', craft='雕填漆器', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-10-25 09:30', capacity=8, price_num=860, cover='/imgs/course/c09.jpg', video=SAMPLE_VIDEO,
         desc='学习髹漆刻纹、填彩磨显的雕填全流程，完成一件雕填漆器小品。',
         status='approved', submit_time='2026-09-03 10:20', review_comment='',
         lessons=build_lessons(DIATIAN_LESSONS, SAMPLE_VIDEO), owner_username='heritage24'),
    dict(name='阳江漆器 · 腰果漆髹涂班', craft='髹漆', stage='体验工作坊', difficulty='零基础', duration='半日',
         schedule='2026-10-12 14:00', capacity=10, price_num=520, cover='/imgs/course/c10.jpg',
         desc='认识腰果漆特性，髹涂一件耐潮耐热的日用漆器，感受阳江漆器的实用之美。',
         status='pending', submit_time='2026-09-03 10:40', review_comment='',
         lessons=build_lessons(YANGJIANG_LESSONS), owner_username='heritage29'),
    dict(name='软螺钿镶嵌 · 贝华入漆体验', craft='螺钿', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-10-19 10:00', capacity=10, price_num=620, cover='/imgs/course/c11.jpg',
         desc='裁贝成画、平贴镶嵌、打磨罩漆，做一只流光溢彩的螺钿漆盘。',
         status='draft', submit_time='', review_comment='',
         lessons=build_lessons(LUODIAN_LESSONS), owner_username='heritage06'),
    dict(name='绛州剔犀 · 云纹剔刻研修班', craft='剔犀', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-10-31 09:30', capacity=8, price_num=1280, cover='/imgs/course/c12.jpg', video=SAMPLE_VIDEO,
         desc='以刀为笔剔开三色漆层，跟随新绛剔犀传承人研习云纹剔刻，完成一件剔犀镇纸。',
         status='approved', submit_time='2026-09-02 09:10', review_comment='',
         lessons=build_lessons(TIXI_LESSONS, SAMPLE_VIDEO), owner_username='heritage05'),
    dict(name='扬州点螺 · 细嵌工艺体验', craft='扬州漆器', stage='体验工作坊', difficulty='进阶', duration='1 天',
         schedule='2026-10-31 14:00', capacity=10, price_num=680, cover='/imgs/course/c13.jpg', video=SAMPLE_VIDEO,
         desc='裁贝如发丝、点嵌成画，在扬州传承人指导下体验点螺细嵌工艺，做一只流光贝盘。',
         status='approved', submit_time='2026-09-02 09:30', review_comment='',
         lessons=build_lessons(DIANLUO_LESSONS, SAMPLE_VIDEO), owner_username='heritage07'),
    dict(name='苏州款彩 · 刻灰填彩挂屏班', craft='款彩', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-11-07 09:30', capacity=8, price_num=1180, cover='/imgs/course/c14.jpg', video=SAMPLE_VIDEO,
         desc='刻灰填彩、山水可触，系统学习苏州款彩工艺，完成一件款彩小挂屏。',
         status='approved', submit_time='2026-09-02 09:50', review_comment='',
         lessons=build_lessons(KUANCAI_LESSONS, SAMPLE_VIDEO), owner_username='heritage08'),
    dict(name='厦门漆线雕 · 盘线贴金体验', craft='漆线雕', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-11-07 14:00', capacity=12, price_num=560, cover='/imgs/course/c15.jpg', video=SAMPLE_VIDEO,
         desc='捻线为笔、盘绕成纹，体验漆线雕盘线贴金，做一块庄严吉祥的漆线平安牌。',
         status='approved', submit_time='2026-09-02 10:10', review_comment='',
         lessons=build_lessons(QIXIANDIAO_LESSONS, SAMPLE_VIDEO), owner_username='heritage10'),
    dict(name='天台夹苎脱胎 · 裱塑入门班', craft='夹苎脱胎', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-11-08 09:30', capacity=8, price_num=1380, cover='/imgs/course/c16.jpg', video=SAMPLE_VIDEO,
         desc='漆麻相合、层层裱塑，跟天台干漆夹苎传承人初探佛像裱塑之法，完成一件夹苎小器。',
         status='approved', submit_time='2026-09-02 10:30', review_comment='',
         lessons=build_lessons(JIAZHU_LESSONS, SAMPLE_VIDEO), owner_username='heritage12'),
    dict(name='宁波泥金彩漆 · 描金堆塑体验', craft='泥金彩漆', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-11-08 14:00', capacity=10, price_num=620, cover='/imgs/course/c17.jpg', video=SAMPLE_VIDEO,
         desc='朱漆为地、真金作华，体验泥金彩漆堆塑与描金，做一件「十里红妆」风小品。',
         status='approved', submit_time='2026-09-02 10:50', review_comment='',
         lessons=build_lessons(NIJIN_LESSONS, SAMPLE_VIDEO), owner_username='heritage13'),
    dict(name='平阳漆器 · 宋韵髹涂工作坊', craft='平阳漆器', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-11-14 09:30', capacity=10, price_num=680, cover='/imgs/course/c18.jpg', video=SAMPLE_VIDEO,
         desc='髹里见宋韵，跟平阳传承人体验素髹打底与揩光，做一件素净温润的髹漆器物。',
         status='approved', submit_time='2026-09-02 11:10', review_comment='',
         lessons=build_lessons(PINGYANG_LESSONS, SAMPLE_VIDEO), owner_username='heritage14'),
    dict(name='坝漆采制 · 走进漆林第一课', craft='制漆', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-11-01 09:30', capacity=12, price_num=520, cover='/imgs/course/c19.jpg', video=SAMPLE_VIDEO,
         desc='「坝漆清如油」——随利川制漆传承人走进漆林看割漆、学滤晒，亲手试髹一器。',
         status='approved', submit_time='2026-09-02 11:30', review_comment='',
         lessons=build_lessons(BAQI_LESSONS, SAMPLE_VIDEO), owner_username='heritage17'),
    dict(name='重庆漆器 · 研磨彩绘班', craft='研磨彩绘', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-11-14 14:00', capacity=8, price_num=1180, cover='/imgs/course/c20.jpg', video=SAMPLE_VIDEO,
         desc='磨出来的彩、养出来的光，系统学习重庆研磨彩绘，完成一件研磨显彩的茶盘。',
         status='approved', submit_time='2026-09-02 11:50', review_comment='',
         lessons=build_lessons(YANMO_LESSONS, SAMPLE_VIDEO), owner_username='heritage18'),
    dict(name='彝族漆器 · 三色手绘体验', craft='彝族漆器', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-11-21 14:00', capacity=12, price_num=480, cover='/imgs/course/c21.jpg', video=SAMPLE_VIDEO,
         desc='一器三色、彝家天工，在凉山传承人指导下以黑红黄手绘日月山川，带走一只三色漆碗。',
         status='approved', submit_time='2026-09-02 12:10', review_comment='',
         lessons=build_lessons(YIZU_LESSONS, SAMPLE_VIDEO), owner_username='heritage19'),
    dict(name='凤翔罩金漆器 · 藏金于漆体验', craft='罩金漆器', stage='体验工作坊', difficulty='进阶', duration='1 天',
         schedule='2026-11-21 09:30', capacity=8, price_num=720, cover='/imgs/course/c22.jpg', video=SAMPLE_VIDEO,
         desc='金在漆里、愈久愈亮，体验凤翔罩金贴箔工序，完成一件罩金小屏牌。',
         status='approved', submit_time='2026-09-02 12:30', review_comment='',
         lessons=build_lessons(ZHAOJIN_LESSONS, SAMPLE_VIDEO), owner_username='heritage23'),
    dict(name='潍坊嵌银髹漆 · 银丝入木工作坊', craft='嵌银髹漆', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-11-15 09:30', capacity=8, price_num=980, cover='/imgs/course/c23.jpg', video=SAMPLE_VIDEO,
         desc='银丝走线、漆木同心，研习潍坊嵌银髹漆刻槽嵌丝工序，完成一件嵌银镇尺。',
         status='approved', submit_time='2026-09-02 12:50', review_comment='',
         lessons=build_lessons(QIANYIN_LESSONS, SAMPLE_VIDEO), owner_username='heritage26'),
    dict(name='上海平磨螺钿 · 素髹揩清班', craft='平磨螺钿', stage='体验工作坊', difficulty='进阶', duration='1 天',
         schedule='2026-11-15 14:00', capacity=10, price_num=760, cover='/imgs/course/c24.jpg', video=SAMPLE_VIDEO,
         desc='贝片入漆、磨平如画，在沪上传承人指导下体验平磨螺钿与素髹揩清，做一件贝华漆器。',
         status='approved', submit_time='2026-09-02 13:10', review_comment='',
         lessons=build_lessons(PINGMO_LESSONS, SAMPLE_VIDEO), owner_username='heritage28'),
    dict(name='潮汕金漆画 · 铁笔描金班', craft='金漆画', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-11-22 09:30', capacity=8, price_num=1080, cover='/imgs/course/c25.jpg',
         desc='铁笔走金、暗室生辉，研习普宁金漆画勾线描金，完成一幅可装框的金漆画小品。',
         status='pending', submit_time='2026-09-03 11:00', review_comment='',
         lessons=build_lessons(JINQIHUA_LESSONS), owner_username='heritage30'),
    dict(name='傣族漆器 · 竹胎髹彩工作坊', craft='髹漆', stage='体验工作坊', difficulty='零基础', duration='1 天',
         schedule='2026-11-28 09:30', capacity=12, price_num=520, cover='/imgs/course/c26.jpg',
         desc='竹骨漆身，体验傣族竹篾编胎与红黑金彩绘，带走一只地道的傣家漆碗。',
         status='draft', submit_time='', review_comment='',
         lessons=build_lessons(DAI_LESSONS), owner_username='heritage31'),
    dict(name='昭通漆刻 · 剔刻填彩班', craft='漆刻', stage='系统课程', difficulty='进阶', duration='6 课时',
         schedule='2026-11-29 09:30', capacity=8, price_num=980, cover='/imgs/course/c27.jpg',
         desc='刻漆如纸、填彩如画，研习昭通漆刻剔刻与填彩晕染，完成一件漆刻作品。',
         status='pending', submit_time='2026-09-03 11:20', review_comment='',
         lessons=build_lessons(QIKE_LESSONS), owner_username='heritage32'),
]

MATERIALS = [
    dict(name='生漆（精制）', spec='500g/瓶', type='material', stock=32, alert_threshold=10, linked_course_name='半日髹漆体验 · 素色茶碗'),
    dict(name='素色茶碗胎', spec='口径 8cm', type='material', stock=48, alert_threshold=12, linked_course_name='半日髹漆体验 · 素色茶碗'),
    dict(name='髹涂牛角刀', spec='大号', type='tool', stock=20, alert_threshold=6, linked_course_name='半日髹漆体验 · 素色茶碗'),
    dict(name='螺钿片套装', spec='含各色贝片', type='material', stock=15, alert_threshold=5, linked_course_name='周末螺钿镶嵌体验'),
    dict(name='大漆主人杯胎', spec='口径 9cm', type='material', stock=26, alert_threshold=8, linked_course_name='周末螺钿镶嵌体验'),
    dict(name='推光粉', spec='细目 500g', type='material', stock=9, alert_threshold=10, linked_course_name='周末螺钿镶嵌体验'),
    dict(name='脱胎木胎套装', spec='杯/碗/盘各一', type='material', stock=18, alert_threshold=5, linked_course_name='髹漆系统课程 · 基础班'),
    dict(name='裱布刮灰套装', spec='含裱布/瓦灰', type='material', stock=22, alert_threshold=6, linked_course_name='髹漆系统课程 · 基础班'),
    dict(name='剔犀刀具套装', spec='含各型号雕刀', type='tool', stock=4, alert_threshold=8, linked_course_name='雕漆系统课程 · 刀法班'),
    dict(name='雕漆练习板', spec='杉木 15×15cm', type='material', stock=30, alert_threshold=8, linked_course_name='雕漆系统课程 · 刀法班'),
    dict(name='推光漆生漆', spec='平遥提庄漆 500g', type='material', stock=24, alert_threshold=8, linked_course_name='平遥推光漆器 · 掌上推光工作坊'),
    dict(name='推光细砖灰', spec='细目 250g', type='material', stock=18, alert_threshold=6, linked_course_name='平遥推光漆器 · 掌上推光工作坊'),
    dict(name='首饰匣实木坯', spec='长 20cm 半成品', type='material', stock=14, alert_threshold=4, linked_course_name='平遥推光漆器 · 掌上推光工作坊'),
    dict(name='脱胎用夏布', spec='细密 1 米/卷', type='material', stock=10, alert_threshold=4, linked_course_name='福州脱胎漆器 · 夹纻制盏班'),
    dict(name='脱胎漆盏模具', spec='杯形胎模', type='tool', stock=12, alert_threshold=5, linked_course_name='福州脱胎漆器 · 夹纻制盏班'),
    dict(name='犀皮多色色漆套', spec='朱/黑/黄/绿', type='material', stock=16, alert_threshold=6, linked_course_name='徽州犀皮漆 · 打埝磨显班'),
    dict(name='打埝稠漆', spec='高稠度 100g', type='material', stock=20, alert_threshold=6, linked_course_name='徽州犀皮漆 · 打埝磨显班'),
    dict(name='楚风彩绘漆(朱黑)', spec='矿物颜料入漆', type='material', stock=12, alert_threshold=5, linked_course_name='楚风漆器 · 髹绘工作坊'),
    dict(name='雕填刻刀套装', spec='含勾/平/尖刀', type='tool', stock=8, alert_threshold=4, linked_course_name='雕填漆器 · 刻纹填彩入门'),
    dict(name='填色彩漆套', spec='入凹槽用色漆', type='material', stock=14, alert_threshold=5, linked_course_name='雕填漆器 · 刻纹填彩入门'),
    dict(name='阳江腰果漆', spec='1kg/罐', type='material', stock=18, alert_threshold=6, linked_course_name='阳江漆器 · 腰果漆髹涂班'),
    dict(name='软螺钿贝片套装', spec='深海贝薄片', type='material', stock=15, alert_threshold=5, linked_course_name='软螺钿镶嵌 · 贝华入漆体验'),
]

STOCK_RECORDS = [
    dict(material_name='生漆（精制）', type='in', qty=20, note='初仓入库', operator='平台管理员', time='2026-08-20 09:30'),
    dict(material_name='剔犀刀具套装', type='in', qty=10, note='初仓入库', operator='平台管理员', time='2026-08-20 09:35'),
    dict(material_name='素色茶碗胎', type='out', qty=2, note='学员材料包领用', operator='平台管理员', time='2026-08-30 15:00'),
    dict(material_name='髹涂牛角刀', type='out', qty=1, note='学员材料包领用', operator='平台管理员', time='2026-08-30 15:00'),
    dict(material_name='雕漆练习板', type='in', qty=30, note='初仓入库', operator='平台管理员', time='2026-09-01 09:00'),
    dict(material_name='推光漆生漆', type='in', qty=24, note='平遥供货商直发', operator='郑寿山', time='2026-09-03 09:10'),
    dict(material_name='脱胎用夏布', type='in', qty=10, note='初仓入库', operator='梁福宁', time='2026-09-03 09:15'),
    dict(material_name='犀皮多色色漆套', type='in', qty=16, note='初仓入库', operator='甘玉成', time='2026-09-03 09:20'),
    dict(material_name='推光细砖灰', type='out', qty=3, note='学员材料包领用', operator='平台管理员', time='2026-09-03 09:30'),
    dict(material_name='素色茶碗胎', type='out', qty=3, note='学员材料包领用', operator='平台管理员', time='2026-09-03 09:35'),
    dict(material_name='脱胎木胎套装', type='out', qty=2, note='学员材料包领用', operator='平台管理员', time='2026-09-03 09:40'),
    dict(material_name='裱布刮灰套装', type='out', qty=2, note='学员材料包领用', operator='平台管理员', time='2026-09-03 09:40'),
    dict(material_name='剔犀刀具套装', type='out', qty=2, note='刀法班学员领用', operator='赵雕', time='2026-09-03 10:00'),
    dict(material_name='生漆（精制）', type='loss', qty=1, note='运输破损报废', operator='平台管理员', time='2026-09-03 10:10'),
]

SHIPMENTS = [
    dict(_student='王木生', _course='半日髹漆体验 · 素色茶碗', _items=['素色茶碗胎', '髹涂牛角刀'],
         status='shipped', company='顺丰速运', tracking_no='SF20260830001', ship_time='2026-08-30 16:00'),
    dict(_student='陈秋白', _course='髹漆系统课程 · 基础班', _items=['脱胎木胎套装', '裱布刮灰套装'],
         status='pending', company='', tracking_no='', ship_time=''),
    dict(_student='吴青', _course='半日髹漆体验 · 素色茶碗', _items=['素色茶碗胎'],
         status='signed', company='中通快递', tracking_no='ZTO20260829001', ship_time='2026-08-29 15:00'),
    dict(_student='徐伯安', _course='半日髹漆体验 · 素色茶碗', _items=['素色茶碗胎', '髹涂牛角刀'],
         status='shipped', company='中通快递', tracking_no='ZTO20260903001', ship_time='2026-09-03 11:00'),
    dict(_student='高启铭', _course='半日髹漆体验 · 素色茶碗', _items=['素色茶碗胎'],
         status='signed', company='韵达快递', tracking_no='YD20260825001', ship_time='2026-08-25 14:00'),
    dict(_student='郑盈盈', _course='髹漆系统课程 · 基础班', _items=['脱胎木胎套装', '裱布刮灰套装'],
         status='shipped', company='顺丰速运', tracking_no='SF20260903002', ship_time='2026-09-03 11:30'),
    dict(_student='罗嘉', _course='髹漆系统课程 · 基础班', _items=['脱胎木胎套装', '裱布刮灰套装'],
         status='pending', company='', tracking_no='', ship_time=''),
    dict(_student='何文远', _course='雕漆系统课程 · 刀法班', _items=['剔犀刀具套装', '雕漆练习板'],
         status='shipped', company='京东物流', tracking_no='JD20260902001', ship_time='2026-09-02 16:00'),
    dict(_student='方奕', _course='雕漆系统课程 · 刀法班', _items=['剔犀刀具套装', '雕漆练习板'],
         status='pending', company='', tracking_no='', ship_time=''),
]

FEEDBACK_MESSAGES = [
    dict(name='王秀兰', contact='138****2211', subject='合作咨询',
         message='您好，我在成都经营一家文创集合店，想咨询千漆作品的批发合作方式。',
         status='handled', reply='感谢关注！已安排专员与您联系，可洽谈代销合作。'),
    dict(name='李国栋', contact='152****3344', subject='课程咨询',
         message='公司团建想预定一场半日髹漆体验，人数约 15 人，请问能否包场？',
         status='handled', reply='可以的，体验课可承接团体包场，稍后商务同事与您对接时间。'),
    dict(name='周女士', contact='158****5566', subject='商品咨询',
         message='请问大漆主人杯什么时候上新？上次活动没抢到。',
         status='new', reply=''),
    dict(name='张先生', contact='guest@example.com', subject='网站建议',
         message='希望周末能多开几个体验班次，工作日上午的班实在排不开。',
         status='new', reply=''),
    dict(name='程校长', contact='133****8899', subject='研学合作',
         message='我是平遥一所中学的美术老师，想带学生来一场平遥推光漆器研学，20 人左右。',
         status='handled', reply='已与推光漆传承人郑老师对接，可为研学专场调整排期。'),
    dict(name='许女士', contact='135****7788', subject='技艺咨询',
         message='看到平台有楚式漆器课程，请问外地学员能线上跟学吗？是否有配套材料包邮寄？',
         status='new', reply=''),
    dict(name='何先生', contact='150****1122', subject='订单咨询',
         message='我的刀法班材料包显示已寄出，但一直没查到物流更新，麻烦看下。',
         status='handled', reply='已核实，快递揽收稍晚，单号 JF20260902001 今早已更新，请留意。'),
    dict(name='徐女士', contact='138****5566', subject='货源咨询',
         message='请问平台能帮非遗传承人代售漆器作品吗？我想把我父亲的推光漆器挂上来。',
         status='new', reply=''),
]

FAVORITES = [
    ('user01', '犀皮描金茶盏'), ('user01', '雕漆云纹果盘'), ('user01', '剔犀云纹茶碗'),
    ('user02', '犀皮描金茶盏'), ('user02', '雕漆云纹果盘'),
    ('user01', '犀皮漆 · 云纹主人杯'), ('user01', '剔犀 · 如意云纹执壶'),
    ('user01', '楚式漆器 · 凤鸟纹圆奁盒'),
    ('user02', '脱胎漆器 · 蝉纹主人杯'), ('user02', '点螺 · 千里江山茶台'),
    ('user02', '软螺钿 · 缠枝莲纹盘'), ('user02', '推光漆 · 描金缠枝首饰匣'),
    ('user03', '嵌银髹漆 · 紫檀笔筒'), ('user03', '阳江漆器 · 提梁食盒'),
    ('user03', '干漆夹苎 · 水月观音'), ('user03', '犀皮漆 · 云纹主人杯'),
    ('user04', '雕漆 · 青绿山水挂屏'), ('user04', '点螺 · 千里江山茶台'),
    ('user04', '脱胎漆器 · 蝉纹主人杯'), ('user04', '剔犀 · 如意云纹执壶'),
]

ADDRESSES = [
    dict(username='user01', receiver='余老板', phone='138****1234', province='四川省', city='成都市',
         district='锦江区', detail='某某路 88 号', is_default=True),
    dict(username='user02', receiver='林小雨', phone='139****5678', province='江苏省', city='扬州市',
         district='广陵区', detail='某某街 12 号', is_default=True),
    dict(username='user03', receiver='唐一苇', phone='137****9988', province='浙江省', city='杭州市',
         district='西湖区', detail='某某路 5 号', is_default=True),
    dict(username='user04', receiver='顾青梧', phone='136****7766', province='北京市', city='北京市',
         district='海淀区', detail='某某大厦 2 层', is_default=True),
]

LOGS = [
    dict(type='login', operator='平台管理员', action='登录系统', detail='账号「admin」以管理员身份登录', time='2026-09-02 09:00'),
    dict(type='login', operator='张守一', action='登录系统', detail='账号「heritage01」以传承人身份登录', time='2026-09-02 09:05'),
    dict(type='review', operator='平台管理员', action='通过技艺档案审核', detail='「雕漆技艺」', time='2026-08-20 10:30'),
    dict(type='create', operator='张守一', action='新增课程', detail='「髹漆系统课程 · 基础班」提交审核', time='2026-08-20 14:20'),
    dict(type='review', operator='平台管理员', action='通过课程审核', detail='「髹漆系统课程 · 基础班」', time='2026-08-20 15:00'),
    dict(type='order', operator='平台管理员', action='订单发货', detail='「犀皮描金茶盏」×2 已发货', time='2026-08-31 20:20'),
    dict(type='ship', operator='平台管理员', action='寄出材料包', detail='学员「王木生」半日髹漆课程材料包已寄出', time='2026-08-30 16:00'),
    dict(type='create', operator='张守一', action='新增作品', detail='「螺钿首饰盒」提交审核', time='2026-09-01 15:35'),
    dict(type='review', operator='平台管理员', action='驳回作品', detail='「款彩山水挂屏」需补充创作理念与细节照片', time='2026-08-29 11:10'),
    dict(type='login', operator='余老板', action='登录系统', detail='账号「user01」以普通用户身份登录', time='2026-09-01 10:00'),
    dict(type='update', operator='平台管理员', action='处理联系留言', detail='已回复留言「合作咨询」', time='2026-09-01 16:20'),
    dict(type='update', operator='张守一', action='修改个人主页', detail='更新了头像与个人简介', time='2026-09-02 09:30'),
    dict(type='review', operator='平台管理员', action='通过技艺档案审核', detail='「平遥推光漆器髹饰技艺」等 30 余条地域漆艺档案', time='2026-09-03 09:00'),
    dict(type='create', operator='平台管理员', action='批量开通传承人账号', detail='为 30 余位地域漆艺大师建档并开通登录账号', time='2026-09-03 09:10'),
    dict(type='login', operator='郑寿山', action='登录系统', detail='账号「heritage04」以传承人身份登录', time='2026-09-03 09:12'),
    dict(type='create', operator='郑寿山', action='新增课程', detail='「平遥推光漆器 · 掌上推光工作坊」提交审核', time='2026-09-03 09:20'),
    dict(type='review', operator='平台管理员', action='通过课程审核', detail='「平遥推光漆器 · 掌上推光工作坊」', time='2026-09-03 09:40'),
    dict(type='create', operator='梁福宁', action='新增作品', detail='「脱胎漆器 · 蝉纹主人杯」提交审核', time='2026-09-03 11:10'),
    dict(type='review', operator='平台管理员', action='通过作品审核', detail='「脱胎漆器 · 蝉纹主人杯」「点螺 · 千里江山茶台」等', time='2026-09-03 11:30'),
    dict(type='order', operator='平台管理员', action='订单发货', detail='「推光漆 · 描金缠枝首饰匣」等 3 单已发货', time='2026-09-03 12:30'),
    dict(type='ship', operator='平台管理员', action='寄出材料包', detail='学员「徐伯安」「郑盈盈」课程材料包已寄出', time='2026-09-03 13:00'),
    dict(type='create', operator='甘玉成', action='提交技艺档案', detail='「徽州漆器髹饰技艺」已提交平台审核', time='2026-09-03 11:00'),
    dict(type='update', operator='沈砚秋', action='更新作品库存', detail='「点螺 · 千里江山茶台」入库 3 件', time='2026-09-03 12:20'),
    dict(type='login', operator='顾青梧', action='登录系统', detail='账号「user04」以普通用户身份登录', time='2026-09-02 12:00'),
]

SYSTEM_CONFIG = dict(
    system=dict(
        systemName='千漆 · 漆器非遗传承平台', logoText='漆', uploadMaxSize=50, uploadMaxCount=9,
        allowVideo=True, allowDoc=True, homeNotice='传承千年漆艺，让非遗走进生活。', icp='蜀ICP备2026000000号',
    ),
    home=dict(
        archives=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        masters=[1, 2, 3, 4, 5, 6, 7, 8],
        featuredCourses=1, featuredProducts=[1, 2],
    ),
)


_WORK_CAT_HINTS = (
    (('杯', '盏', '碗', '壶'), '茶器'),
    (('屏', '挂屏', '架'), '陈设'),
    (('盘', '盒', '匣', '奁', '罐', '筒', '盆', '缸'), '日用'),
)
_WORK_GLYPH_HINTS = (
    ('杯', '杯'), ('盏', '盏'), ('碗', '碗'), ('壶', '壶'), ('瓶', '瓶'),
    ('屏', '屏'), ('盘', '盘'), ('盒', '盒'), ('匣', '匣'), ('奁', '奁'),
    ('罐', '罐'), ('筒', '筒'), ('台', '台'), ('笔', '笔'),
)


def _skill_work_names(skill):
    return [t.strip() for t in (skill.works or '').split('｜') if t.strip()]


def _guess_work_category(name):
    for keys, cat in _WORK_CAT_HINTS:
        if any(k in name for k in keys):
            return cat
    return '摆件'


def _guess_work_glyph(name):
    for k, g in _WORK_GLYPH_HINTS:
        if k in name:
            return g
    return '作'


def _make_work_product(skill, used_names):
    toks = _skill_work_names(skill) or [f'{skill.name} · 代表作品']
    base = toks[0]
    name, n = base, 2
    while name in used_names:
        name = f'{base}{n}'
        n += 1
    used_names.add(name)
    price = [298, 398, 498, 668, 888][len(name) % 5]
    return Product.objects.create(
        owner_id=skill.owner_id,
        glyph=_guess_work_glyph(name), name=name,
        craft=skill.category or '', category=_guess_work_category(name),
        material='天然大漆 · 手工髹作', size='',
        inheritor=skill.owner.name or '', level=skill.level or '',
        saleable=True, price=price, cost_price=int(price * 0.4),
        stock=9, alert_threshold=5,
        cover='', images=[],
        story=f'「{skill.name}」代表作品，以天然大漆髹饰而成，一器一工，温润耐藏。',
        highlights=[f'{skill.level}技艺 · 手工髹作', '天然大漆 · 精工打磨'],
        status='approved', flag='', submit_time=skill.submit_time or '',
        review_comment='',
    )


def _skill_difficulty(skill):
    text = ' '.join([
        skill.name or '', skill.category or '', skill.abstract or '', skill.desc or '',
    ])
    if any(k in text for k in (
        '雕漆', '剔犀', '剔红', '款彩', '雕填', '漆线雕', '泥金彩漆',
        '夹苎', '夹纻', '点螺', '百宝嵌', '镶嵌', '雕花填彩', '堆塑',
    )):
        return '高级'
    if any(k in text for k in ('制漆', '生漆采割', '采割精制', '割漆')):
        return '零基础'
    return '进阶'


def _skill_school(skill):
    text = ' '.join([skill.name or '', skill.category or '', skill.region or '', skill.origin or ''])
    if '彝族' in text:
        return '彝族漆器'
    if any(k in text for k in ('制漆', '生漆采割', '采割精制', '割漆')):
        return '鄂西制漆'
    for keys, school in (
        ('北京市|北京|河北|廊坊', '京作'),
        ('苏州', '苏作'),
        ('江苏|扬州|上海', '扬作'),
        ('山西|平遥|新绛|稷山', '晋作'),
        ('四川|成都|重庆', '蜀作'),
        ('福建|福州|厦门|泉州', '闽作'),
        ('浙江|宁波|天台|温州', '浙作'),
        ('安徽|黄山|徽州', '徽作'),
        ('湖北|荆州', '楚作'),
        ('江西|鄱阳|婺源', '赣作'),
        ('陕西|甘肃|凤翔|天水', '秦作'),
        ('山东|潍坊', '鲁作'),
        ('广西|桂林', '桂作'),
        ('广东|阳江|普宁', '广作'),
        ('云南|傣族|昭通', '滇作'),
        ('河南|沁阳', '中原'),
        ('黑龙江|哈尔滨', '关东'),
    ):
        if any(k in text for k in keys.split('|')):
            return school
    return ''


def fill_course_schedule(course):
    lessons = course.lessons or []
    sched = (course.schedule or '').strip()
    start = None
    try:
        if len(sched) >= 10:
            start = date.fromisoformat(sched[:10])
    except ValueError:
        start = None
    if not (start and lessons):
        return False
    parts = sched.split(' ')
    t = parts[1].strip() if len(parts) > 1 and parts[1].strip() else '14:00'
    n = len(lessons)
    step = max(1, round(28 / n))
    venue = ONLINE_VENUES[sum(ord(ch) for ch in (course.name or '')) % len(ONLINE_VENUES)]
    new_lessons = []
    changed = False
    for i, les in enumerate(lessons):
        les = dict(les)
        if not (les.get('scheduleDate') or '').strip():
            les['scheduleDate'] = (start + timedelta(days=step * i)).isoformat()
            changed = True
        if not (les.get('scheduleTime') or '').strip():
            les['scheduleTime'] = t
            changed = True
        if not (les.get('address') or '').strip():
            les['address'] = venue
            changed = True
        new_lessons.append(les)
    if changed:
        course.lessons = new_lessons
    if not (course.end_date or '').strip():
        course.end_date = (start + timedelta(days=step * (n - 1))).isoformat()
        changed = True
    return changed


def _bind_skill_works(prod_map):
    used_names = set(prod_map)
    linked = 0
    for skill in Skill.objects.filter(status__in=('approved', 'offline')).order_by('id'):
        own = list(Product.objects.filter(owner_id=skill.owner_id, status='approved').order_by('id'))
        if not own:
            p = _make_work_product(skill, used_names)
            prod_map[p.name] = p
            own = [p]
        wset = set(_skill_work_names(skill))
        matched = [p for p in own if p.name in wset] or own[:3]
        skill.works_product_ids = [p.id for p in matched]
        skill.save(update_fields=['works_product_ids'])
        linked += 1
    return linked


def run():
    OperationLog.objects.all().delete()
    SystemConfig.objects.all().delete()
    FeedbackMessage.objects.all().delete()
    Shipment.objects.all().delete()
    StockRecord.objects.all().delete()
    Material.objects.all().delete()
    Course.objects.all().delete()
    ProductStockRecord.objects.all().delete()
    Favorite.objects.all().delete()
    Product.objects.all().delete()
    Skill.objects.all().delete()
    Student.objects.all().delete()
    Order.objects.all().delete()
    Address.objects.all().delete()
    HeritageProfile.objects.all().delete()
    TrainingRecord.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    Admin.objects.filter(is_superuser=False).delete()
    Inheritor.objects.filter(is_superuser=False).delete()

    role_model = {'user': User, 'admin': Admin, 'heritage': Inheritor}
    for a in ACCOUNTS:
        a = dict(a)
        role = a.pop('role')
        role_model[role].objects.create_user(password=ADMIN_PWD, **a)
    username2user = {}
    for role, M in role_model.items():
        for obj in M.objects.all():
            username2user[(role, obj.username)] = obj

    def get_acct(role, uname):
        return username2user.get((role, uname))

    for p in PROFILES:
        p = dict(p)
        uname = p.pop('username')
        HeritageProfile.objects.create(account=get_acct('heritage', uname), **p)

    for o in ORDERS:
        o = dict(o)
        Order.objects.create(
            seller=get_acct('heritage', o.pop('seller_username', None)),
            buyer_user=get_acct('user', o.pop('buyer_username', None)),
            **o,
        )

    for c in COURSES:
        c = dict(c)
        uname = c.pop('owner_username')
        Course.objects.create(owner=get_acct('heritage', uname), **c)
    course_by_name = {c.name: c for c in Course.objects.all()}

    for sk in SKILLS:
        sk = dict(sk)
        uname = sk.pop('owner_username')
        Skill.objects.create(owner=get_acct('heritage', uname), **sk)
    for sk in Skill.objects.all():
        blanks = {}
        if not (sk.difficulty or '').strip():
            blanks['difficulty'] = _skill_difficulty(sk)
        if not (sk.school or '').strip():
            blanks['school'] = _skill_school(sk)
        if blanks:
            Skill.objects.filter(pk=sk.pk).update(**blanks)

    for pr in PRODUCTS:
        pr = dict(pr)
        uname = pr.pop('owner_username')
        Product.objects.create(owner=get_acct('heritage', uname), **pr)
    prod_map = {p.name: p for p in Product.objects.all()}
    _linked_skills = _bind_skill_works(prod_map)

    for s_ in STUDENTS:
        s_ = dict(s_)
        cname = s_.pop('course_name', None)
        cobj = course_by_name.get(cname) if cname else None
        s_['course_id'] = cobj.id if cobj else 0
        s_['course_name'] = cname or ''
        s_['user'] = get_acct('user', s_.pop('username', None))
        Student.objects.create(**s_)

    for c in Course.objects.all():
        c.enrolled = Student.objects.filter(
            course_id=c.id, status__in=('ongoing', 'done')
        ).count()
        fields = ['enrolled']
        if fill_course_schedule(c):
            fields += ['lessons', 'end_date']
        c.save(update_fields=fields)

    mat_map = {}
    for m in MATERIALS:
        m = dict(m)
        cname = m.get('linked_course_name')
        cobj = course_by_name.get(cname) if cname else None
        m['linked_course_id'] = cobj.id if cobj else 0
        m['linked_course_name'] = cname or ''
        mat_map[m['name']] = Material.objects.create(**m)
    for r in STOCK_RECORDS:
        r = dict(r)
        mat = mat_map.get(r.pop('material_name'))
        StockRecord.objects.create(material=mat, material_name=mat.name if mat else '', **r)

    st_map = {s.name: s for s in Student.objects.all()}
    for sh in SHIPMENTS:
        sh = dict(sh)
        st = st_map.get(sh.pop('_student'))
        cobj = course_by_name.get(sh.pop('_course'))
        items = sh.pop('_items')
        sh['student_id'] = st.id if st else 0
        sh['student_name'] = st.name if st else ''
        sh['course_id'] = cobj.id if cobj else 0
        sh['course_name'] = cobj.name if cobj else ''
        sh['items'] = [
            {'materialId': mat_map[m].id if m in mat_map else 0, 'materialName': m, 'qty': 1}
            for m in items
        ]
        Shipment.objects.create(**sh)

    for r in PRODUCT_STOCK_RECORDS:
        r = dict(r)
        pname = r.pop('product_name')
        ProductStockRecord.objects.create(product=prod_map.get(pname), product_name=pname, **r)

    for tr in TRAINING_RECORDS:
        tr = dict(tr)
        cname = tr.pop('course_name')
        TrainingRecord.objects.create(course=course_by_name.get(cname), course_name=cname, **tr)

    for fm in FEEDBACK_MESSAGES:
        FeedbackMessage.objects.create(**fm)

    for uname, pname in FAVORITES:
        u = get_acct('user', uname)
        if u and pname in prod_map:
            Favorite.objects.create(user=u, product=prod_map[pname])

    for ad in ADDRESSES:
        ad = dict(ad)
        uname = ad.pop('username')
        Address.objects.create(user=get_acct('user', uname), **ad)

    for l in LOGS:
        OperationLog.objects.create(**l)

    home_cfg = dict(SYSTEM_CONFIG['home'])
    home_cfg['archives'] = list(Skill.objects.filter(status='approved').values_list('id', flat=True))
    home_cfg['masters'] = list(HeritageProfile.objects.filter(status='active').values_list('id', flat=True))
    approved_course = Course.objects.filter(status='approved').order_by('id').first()
    home_cfg['featuredCourses'] = approved_course.id if approved_course else 1
    home_cfg['featuredProducts'] = list(Product.objects.filter(status='approved').values_list('id', flat=True))
    SystemConfig.objects.create(key='system', value=SYSTEM_CONFIG['system'])
    SystemConfig.objects.create(key='home', value=home_cfg)

    _bodies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skill_bodies.json')
    if os.path.exists(_bodies_path):
        with open(_bodies_path, encoding='utf-8') as _bf:
            _bodies = json.load(_bf)
        _applied = 0
        for _bname, _bbody in _bodies.items():
            _bqs = Skill.objects.filter(name=_bname)
            if _bqs.exists():
                _bqs.update(body=_bbody)
                _applied += 1
        print(f'技艺正文: 预填 {_applied} 条详情正文（skill_bodies.json）')

    _imgs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skill_images_manifest.json')
    if os.path.exists(_imgs_path):
        with open(_imgs_path, encoding='utf-8') as _if:
            _imgs = json.load(_if)
        _applied = 0
        for _bname, _slot in _imgs.items():
            _iqs = Skill.objects.filter(name=_bname)
            if not _iqs.exists():
                continue
            _sk = _iqs.first()
            _body = dict(_sk.body or {})
            if _slot.get('cover'):
                _sk.image = _slot['cover']
            _steps = list(_body.get('steps', []))
            for _i, _u in enumerate(_slot.get('steps', [])):
                if _u and _i < len(_steps):
                    _st = dict(_steps[_i]); _st['image'] = _u; _steps[_i] = _st
            if _steps:
                _body['steps'] = _steps
            _cards = list(_body.get('cards', []))
            for _i, _u in enumerate(_slot.get('cards', [])):
                if _u and _i < len(_cards):
                    _ca = dict(_cards[_i]); _ca['image'] = _u; _cards[_i] = _ca
            if _cards:
                _body['cards'] = _cards
            _sk.body = _body
            _sk.save(update_fields=['image', 'body'])
            _applied += 1
        print(f'技艺配图: 预填 {_applied} 门封面/工序/纪实图（skill_images_manifest.json）')

    print('=== 灌入结果 ===')
    print(f'学员账号: {User.objects.count()}  管理员: {Admin.objects.count()}  传承人账号: {Inheritor.objects.count()}')
    print(f'传承人档案: {HeritageProfile.objects.count()}')
    print(f'订单: {Order.objects.count()}  地址: {Address.objects.count()}')
    print(f'学员: {Student.objects.count()}  培训记录: {TrainingRecord.objects.count()}')
    print(f'技艺: {Skill.objects.count()}  作品: {Product.objects.count()}  收藏: {Favorite.objects.count()}')
    print(f'技艺绑定代表作: {_linked_skills} 项公开技艺已勾选')
    print(f'作品流水: {ProductStockRecord.objects.count()}')
    print(f'课程: {Course.objects.count()}  物料: {Material.objects.count()}  流水: {StockRecord.objects.count()}  邮寄: {Shipment.objects.count()}')
    print(f'留言: {FeedbackMessage.objects.count()}  日志: {OperationLog.objects.count()}')
    lv = {s.level: Skill.objects.filter(status='approved', level=s.level).count() for s in Skill.objects.filter(status='approved')}
    print(f'已通过技艺按级别分布: {lv}')
    for c in Course.objects.filter(status='approved'):
        print(f'  - 已通过课程「{c.name}」enrolled={c.enrolled} 课时={len(c.lessons)}')
    print('灌入完成')


if __name__ == '__main__':
    run()
