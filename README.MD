# 停车场收费系统

基于 Flask + Vue 的停车场收费系统，包含车位状态监控、月卡办理、临时停车计费和电子发票开具。

## 功能模块

- 车位状态监控：查看车位总数、空闲、占用、预约、维护状态，支持更新车位状态。
- 月卡办理：登记车主、手机号、车牌、有效期和费用，支持月卡状态维护。
- 临时停车计费：登记车辆入场、按 15 分钟免费和 8 元/小时规则试算，支持离场结算。
- 电子发票开具：基于已结算停车订单生成电子发票记录。

## 项目结构

```text
backend/
  app/
    routes/       Flask 蓝图接口
    services/     计费、发票等业务服务
    database.py   SQLite 初始化和连接
  run.py
  Dockerfile
frontend/
  src/
    api/          前端请求封装
    components/   通用组件
    pages/        业务页面
    styles/       全局样式
  Dockerfile
  nginx.conf
docker-compose.yml
```

## 本地开发

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

前端：

```bash
cd frontend
npm install
npm run dev
```

访问 `http://127.0.0.1:5173`，后端接口为 `http://127.0.0.1:5000/api`。

## Docker Compose 启动

```bash
docker compose up --build
```

访问 `http://127.0.0.1:8080`。前端 Nginx 会将 `/api` 代理到后端 Flask 服务。

## 验证接口

```bash
curl http://127.0.0.1:5000/api/health
curl http://127.0.0.1:5000/api/spaces
```
