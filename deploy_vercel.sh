#!/bin/bash

# Vercel 部署脚本
echo "开始 Vercel 部署..."

# 清理缓存
echo "清理本地缓存..."
npm cache clean --force 2>/dev/null || true
pip cache purge 2>/dev/null || true

# 检查前端构建
echo "测试前端构建..."
cd frontend
npm ci
npm run build
if [ $? -ne 0 ]; then
    echo "前端构建失败，请检查错误信息"
    exit 1
fi
cd ..

# 部署到 Vercel
echo "开始部署到 Vercel..."
vercel --prod

echo "部署完成！"