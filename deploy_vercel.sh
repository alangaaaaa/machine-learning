#!/bin/bash

# Vercel 优化部署脚本
echo "开始 Vercel 优化部署..."

# 清理不必要的文件
echo "清理项目文件..."
rm -rf logs/
rm -rf backend/__pycache__/
rm -rf frontend/node_modules/.cache/
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name ".DS_Store" -delete

# 清理缓存
echo "清理本地缓存..."
npm cache clean --force 2>/dev/null || true
pip cache purge 2>/dev/null || true

# 检查前端构建
echo "测试前端构建..."
cd frontend
# 只安装生产依赖
npm ci --only=production
npm run build
if [ $? -ne 0 ]; then
    echo "前端构建失败，请检查错误信息"
    exit 1
fi
cd ..

# 显示部署包大小
echo "检查部署包大小..."
du -sh . | head -1

# 部署到 Vercel
echo "开始部署到 Vercel..."
vercel --prod

echo "部署完成！"