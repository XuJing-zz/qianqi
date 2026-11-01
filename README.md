# 千漆 · 漆器技艺教学与文创进销存管理系统

一个面向漆器非遗场景的 Web 平台，把**技艺展示、课程培训、文创销售**放在同一套系统里。
项目采用前后端分离架构：Django + DRF 提供接口，Vue 3 构建学员端、传承人工作台和管理后台三套界面。

## 功能概览

### 学员端

- 浏览技艺档案与传承人主页，按级别、门类、难度、流派、地区筛选
- 报名培训课程、在线学习、查看报名状态
- 选购文创作品，下单、支付、查看物流
- 个人中心：我的订单、我的报名、我的学习、收藏、收货地址

### 传承人工作台

- 技艺档案的申报、编辑、提交审核与上下架
- 课程创建、课时与教学视频维护
- 作品上架、库存出入库与预警
- 学员报名审核、培训记录管理

### 管理后台

- 技艺、课程、作品、课时视频的审核与下架
- 订单管理、发货与物流填写
- 学员、传承人、账号管理
- 系统配置（站点信息、首页展示内容）、操作日志、留言处理

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vue Router、Vite、Element Plus |
| 通信 | 原生 Fetch 封装、JWT（access + refresh） |
| 后端 | Python 3、Django 6、Django REST Framework |
| 数据库 | MySQL 8（utf8mb4） |
| 鉴权 | SimpleJWT，多账号表认证 + 角色权限 |

## 目录结构

```
qianqi/
├─ backend/                 Django 后端
│  ├─ config/               配置与总路由
│  ├─ accounts/             学员 / 管理员 / 传承人三张账号表、JWT 认证与权限
│  ├─ heritage/             传承人档案与荣誉证书
│  ├─ skills/               技艺档案
│  ├─ courses/              课程、课时与视频审核
│  ├─ students/             报名记录与培训记录
│  ├─ products/             文创作品、库存流水、收藏
│  ├─ orders/               订单、订单状态日志、收货地址
│  ├─ inventory/            物料库存与邮寄记录
│  ├─ system/               系统配置、操作日志、留言
│  ├─ common/               分页、上传、日志等公共能力
│  └─ media/                上传的图片与视频
└─ frontend/                Vue 3 前端
   ├─ src/views/user/       学员端页面
   ├─ src/views/console/    传承人工作台
   ├─ src/views/admin/      管理后台
   ├─ src/api/              接口封装
   └─ src/store/            全局状态
```

## 本地运行

### 1. 准备数据库

创建 MySQL 数据库和账号：

```sql
CREATE DATABASE qianqi DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'qianqi_user'@'127.0.0.1' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON qianqi.* TO 'qianqi_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

### 2. 启动后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# 打开 .env，填写数据库密码和 DJANGO_SECRET_KEY

python manage.py migrate
python manage.py init_demo_data   # 可选：写入演示数据（会清空并重建业务数据）
python manage.py runserver 8001
```

后端地址：`http://127.0.0.1:8001`

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：`http://localhost:5173`，开发服务器已把 `/api` 代理到 `http://127.0.0.1:8001`。

## 环境变量

后端从 `backend/.env` 读取配置，密钥不写进代码仓库。

| 变量 | 说明 |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django 密钥，必须随机生成 |
| `DJANGO_DEBUG` | 是否开启调试，默认 `True` |
| `DJANGO_ALLOWED_HOSTS` | 允许访问的域名，逗号分隔 |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | 数据库名与账号 |
| `DB_HOST` / `DB_PORT` | 数据库地址与端口 |

## 演示账号

| 角色 | 账号 | 密码 |
| --- | --- | --- |
| 管理员 | `admin` | `123456` |
| 传承人 | `heritage01` | `123456` |
| 学员 | `user01` | `123456` |

## 主要接口

| 前缀 | 说明 |
| --- | --- |
| `/api/accounts/` | 登录、注册、账号管理 |
| `/api/heritage/` | 传承人档案与证书上传 |
| `/api/skills/` | 技艺档案 |
| `/api/courses/` | 课程、课时与视频审核 |
| `/api/students/` | 报名与培训记录 |
| `/api/products/` | 文创作品与库存 |
| `/api/orders/` | 订单与地址 |
| `/api/inventory/` | 物料库存与邮寄 |
| `/api/system/` | 系统配置、日志与留言 |

登录成功后会返回 `access` 与 `refresh` 两个 Token，请求时在请求头携带
`Authorization: Bearer <access>`。

## 说明

- 支付为演示流程，不接入真实支付渠道。
- 上传文件保存在 `backend/media/`，该目录不纳入版本管理。
- 演示数据可通过 `python manage.py init_demo_data` 重建。
