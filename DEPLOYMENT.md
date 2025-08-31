# Vercel部署指南

## 快速部署

### 1. 自动部署（推荐）
```bash
# 运行自动部署脚本
./deploy.sh
```

### 2. 手动部署

#### 步骤1：部署后端
```bash
cd backend
vercel --prod --yes
```

#### 步骤2：获取后端URL
```bash
vercel ls
# 记下后端URL，例如：https://your-backend.vercel.app
```

#### 步骤3：配置前端环境变量
```bash
cd frontend
echo "REACT_APP_API_URL=https://your-backend.vercel.app" > .env.production
```

#### 步骤4：构建并部署前端
```bash
npm run build
vercel --prod --yes
```

## 部署前检查清单

- [ ] 确保 `backend/svm_model.pkl` 文件存在
- [ ] 确保 `backend/original_data_samples.xlsx` 文件存在
- [ ] 确保已安装Vercel CLI：`npm install -g vercel`
- [ ] 确保已登录Vercel：`vercel login`

## 部署后验证

1. **检查后端API**
   ```bash
   curl https://your-backend.vercel.app/api/health
   ```

2. **检查前端页面**
   - 访问前端URL
   - 测试文件上传功能
   - 测试预测功能

## 故障排除

### 常见问题

1. **模型文件过大**
   - Vercel有50MB文件大小限制
   - 如果模型文件过大，考虑使用模型压缩或云存储

2. **依赖安装失败**
   - 检查 `requirements.txt` 中的版本兼容性
   - 确保所有依赖都支持Python 3.9+

3. **环境变量问题**
   - 确保前端正确配置了 `REACT_APP_API_URL`
   - 检查后端URL是否可访问

### 调试命令

```bash
# 查看部署状态
vercel ls

# 查看部署日志
vercel logs

# 重新部署
vercel --prod --force
```

## 性能优化

1. **模型优化**
   - 使用模型压缩技术
   - 考虑使用更轻量级的模型

2. **前端优化**
   - 启用代码分割
   - 优化图片和静态资源

3. **API优化**
   - 添加缓存机制
   - 优化数据处理流程

## 安全注意事项

1. **API安全**
   - 添加请求频率限制
   - 验证文件类型和大小
   - 添加CORS配置

2. **数据安全**
   - 不存储敏感数据
   - 使用HTTPS传输
   - 添加输入验证

## 监控和维护

1. **性能监控**
   - 使用Vercel Analytics
   - 监控API响应时间

2. **错误监控**
   - 设置错误日志
   - 配置告警机制

3. **定期更新**
   - 更新依赖包
   - 更新模型版本
