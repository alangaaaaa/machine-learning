#!/bin/bash

echo "🚀 开始部署SVM医疗预测系统到Vercel..."

# 检查是否安装了Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ 未安装Vercel CLI，正在安装..."
    sudo npm install -g vercel
fi

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ 前端依赖安装失败，尝试修复..."
    npm install --legacy-peer-deps
    if [ $? -ne 0 ]; then
        echo "❌ 前端依赖安装失败，请检查package.json中的依赖版本"
        exit 1
    fi
fi

# 构建前端
echo "📦 构建前端应用..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 前端构建失败，请检查构建日志"
    exit 1
fi
echo "✅ 前端构建成功"

# 部署后端
echo "📦 部署后端到Vercel..."
cd ../backend

# 安装后端依赖
echo "📦 安装后端依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 后端依赖安装失败，请检查requirements.txt"
    exit 1
fi

# 检查是否有模型文件
if [ ! -f "svm_model.pkl" ]; then
    echo "❌ 未找到svm_model.pkl文件"
    exit 1
fi

# 部署后端
echo "📦 执行后端部署..."
vercel --prod --yes
if [ $? -ne 0 ]; then
    echo "❌ 后端部署失败，尝试使用--force选项..."
    vercel --prod --force --yes
    if [ $? -ne 0 ]; then
        echo "❌ 后端部署失败，请检查Vercel配置和日志"
        exit 1
    fi
fi

# 获取后端URL
BACKEND_URL=$(vercel ls | grep svm-medical-prediction | head -1 | awk '{print $2}')
echo "✅ 后端已部署到: $BACKEND_URL"

# 部署前端
echo "📦 部署前端到Vercel..."
cd ../frontend

# 创建环境变量文件
echo "REACT_APP_API_URL=$BACKEND_URL" > .env.production

# 同时在项目根目录创建环境变量文件
cd ..
echo "REACT_APP_API_URL=$BACKEND_URL" > .env.production
cd frontend

# 重新构建前端（包含环境变量）
echo "📦 使用环境变量重新构建前端..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 前端重新构建失败，请检查环境变量配置"
    exit 1
fi

# 回到项目根目录部署前端
cd ..

# 部署前端
echo "📦 执行前端部署..."
vercel --prod --yes
if [ $? -ne 0 ]; then
    echo "❌ 前端部署失败，尝试使用--force选项..."
    vercel --prod --force --yes
    if [ $? -ne 0 ]; then
        echo "❌ 前端部署失败，请检查Vercel配置和日志"
        exit 1
    fi
fi

# 获取前端URL
FRONTEND_URL=$(vercel ls | grep svm-medical-prediction-frontend | head -1 | awk '{print $2}')

echo "🎉 部署完成！"
echo "前端地址: $FRONTEND_URL"
echo "后端地址: $BACKEND_URL"
echo ""
echo "📋 部署信息："
echo "- 前端已配置API地址: $BACKEND_URL"
echo "- 后端包含SVM模型和数据处理逻辑"
echo "- 支持CSV和Excel文件上传"
echo "- 实时预测功能已启用"
