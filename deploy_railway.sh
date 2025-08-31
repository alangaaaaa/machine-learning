#!/bin/bash

echo "🚀 开始部署SVM医疗预测系统到Railway + Vercel..."

# 检查是否安装了Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ 未安装Railway CLI，正在安装..."
    npm install -g @railway/cli
fi

# 检查是否安装了Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ 未安装Vercel CLI，正在安装..."
    sudo npm install -g vercel
fi

# 检查模型文件
echo "📋 检查必要文件..."
if [ ! -f "backend/svm_model.pkl" ]; then
    echo "❌ 未找到svm_model.pkl文件"
    exit 1
fi

if [ ! -f "backend/original_data_samples.xlsx" ]; then
    echo "❌ 未找到original_data_samples.xlsx文件"
    exit 1
fi

echo "✅ 所有必要文件检查通过"

# 部署后端到Railway
echo "📦 部署后端到Railway..."
cd backend

# 登录Railway（如果需要）
echo "🔐 请确保已登录Railway..."
railway login

# 初始化并部署
railway init --yes
railway up

# 获取后端URL
echo "⏳ 等待部署完成..."
sleep 10
BACKEND_URL=$(railway status | grep "URL" | awk '{print $2}')

if [ -z "$BACKEND_URL" ]; then
    echo "❌ 无法获取后端URL"
    exit 1
fi

echo "✅ 后端已部署到: $BACKEND_URL"

# 部署前端到Vercel
echo "📦 部署前端到Vercel..."
cd ../frontend

# 创建环境变量文件
echo "REACT_APP_API_URL=$BACKEND_URL" > .env.production

# 构建前端
echo "🔨 构建前端应用..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 前端构建失败"
    exit 1
fi

# 部署前端
vercel --prod --yes
if [ $? -ne 0 ]; then
    echo "❌ 前端部署失败"
    exit 1
fi

# 获取前端URL
FRONTEND_URL=$(vercel ls | grep svm-medical-prediction-frontend | head -1 | awk '{print $2}')

echo "🎉 部署完成！"
echo ""
echo "📋 部署信息："
echo "前端地址: $FRONTEND_URL"
echo "后端地址: $BACKEND_URL"
echo ""
echo "🔧 配置信息："
echo "- 前端已配置API地址: $BACKEND_URL"
echo "- 后端包含SVM模型和数据处理逻辑"
echo "- 支持CSV和Excel文件上传"
echo "- 实时预测功能已启用"
echo ""
echo "📝 使用说明："
echo "1. 访问前端地址开始使用"
echo "2. 上传包含必要特征的CSV或Excel文件"
echo "3. 点击预测按钮获得结果"
echo ""
echo "🔍 故障排除："
echo "- 如果遇到问题，请检查Railway和Vercel控制台"
echo "- 确保所有环境变量配置正确"
