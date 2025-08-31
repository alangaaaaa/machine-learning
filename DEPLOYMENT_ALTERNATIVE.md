# 替代部署方案

由于Vercel对Python科学计算库的大小限制，我们推荐使用以下部署方案：

## 方案1：Railway + Vercel（推荐）

### 后端部署到Railway

1. **注册Railway账户**
   - 访问 https://railway.app
   - 使用GitHub账户登录

2. **部署后端**
   ```bash
   # 安装Railway CLI
   npm install -g @railway/cli
   
   # 登录Railway
   railway login
   
   # 部署后端
   cd backend
   railway init
   railway up
   ```

3. **获取后端URL**
   - 在Railway控制台查看部署的URL
   - 例如：https://your-app.railway.app

### 前端部署到Vercel

1. **配置环境变量**
   ```bash
   cd frontend
   echo "REACT_APP_API_URL=https://your-app.railway.app" > .env.production
   ```

2. **构建并部署前端**
   ```bash
   npm run build
   vercel --prod --yes
   ```

## 方案2：Render + Vercel

### 后端部署到Render

1. **注册Render账户**
   - 访问 https://render.com
   - 使用GitHub账户登录

2. **创建Web Service**
   - 连接GitHub仓库
   - 选择Python环境
   - 设置启动命令：`python app.py`

3. **配置环境变量**
   - 在Render控制台设置环境变量
   - 确保端口配置正确

## 方案3：Heroku + Vercel

### 后端部署到Heroku

1. **安装Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **创建Procfile**
   ```bash
   echo "web: python app.py" > backend/Procfile
   ```

3. **部署到Heroku**
   ```bash
   cd backend
   heroku create your-app-name
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## 方案4：本地部署 + Vercel前端

如果您有服务器或VPS，也可以：

1. **在服务器上部署后端**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 启动服务
   python app.py
   ```

2. **配置域名和SSL**
   - 使用Nginx作为反向代理
   - 配置SSL证书

3. **前端部署到Vercel**
   - 配置API地址指向您的服务器

## 推荐方案对比

| 平台 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| Railway | 免费额度大，支持科学计算库 | 需要信用卡验证 | ⭐⭐⭐⭐⭐ |
| Render | 免费额度大，部署简单 | 冷启动较慢 | ⭐⭐⭐⭐ |
| Heroku | 稳定可靠 | 免费额度有限 | ⭐⭐⭐ |
| 本地服务器 | 完全控制 | 需要维护 | ⭐⭐ |

## 快速部署脚本

### Railway部署脚本
```bash
#!/bin/bash
echo "🚀 部署到Railway..."

# 安装Railway CLI
npm install -g @railway/cli

# 部署后端
cd backend
railway login
railway init
railway up

# 获取后端URL
BACKEND_URL=$(railway status | grep "URL" | awk '{print $2}')

# 部署前端
cd ../frontend
echo "REACT_APP_API_URL=$BACKEND_URL" > .env.production
npm run build
vercel --prod --yes

echo "🎉 部署完成！"
echo "后端地址: $BACKEND_URL"
```

## 故障排除

### 常见问题

1. **端口配置问题**
   - 确保使用环境变量PORT
   - 修改app.py中的端口配置

2. **环境变量问题**
   - 在平台控制台设置环境变量
   - 确保前端正确配置API地址

3. **依赖安装问题**
   - 检查requirements.txt版本兼容性
   - 使用平台推荐的Python版本

### 调试命令

```bash
# Railway
railway logs
railway status

# Render
render logs
render status

# Heroku
heroku logs --tail
heroku status
```
