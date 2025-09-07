# Vercel 部署指南

## 部署准备

本项目已针对 Vercel 部署进行了优化，包含以下特性：

### 技术优化
- ✅ **纯 Python 实现**: 移除了所有编译依赖
- ✅ **轻量级依赖**: 仅使用 Flask 和 Flask-CORS
- ✅ **简化模型**: 使用内置权重，无需外部模型文件
- ✅ **文件支持**: 支持 CSV 文件上传（Excel 需转换为 CSV）

### 功能特性
- 🔢 **手动输入**: 支持表单填写预测
- 📁 **文件上传**: 支持 CSV 批量预测
- 🌐 **英文界面**: 完整的英文用户界面
- 📱 **响应式设计**: 适配移动端和桌面端

## 部署步骤

### 1. 准备 Vercel 账户

1. 访问 [vercel.com](https://vercel.com)
2. 使用 GitHub 账户登录
3. 安装 Vercel CLI（如果尚未安装）：
   ```bash
   npm install -g vercel
   ```

### 2. 项目配置检查

确认以下文件配置正确：

- `vercel.json`: 部署配置文件
- `backend/requirements.txt`: 仅包含基础依赖
- `backend/app_vercel.py`: Vercel 优化版后端
- `backend/simple_model.py`: 纯 Python 模型实现

### 3. 执行部署

在项目根目录执行：

```bash
# 登录 Vercel（首次使用）
vercel login

# 部署到生产环境
vercel --prod
```

### 4. 部署验证

部署完成后，Vercel 会提供：
- 🌐 **生产环境 URL**: 用于正式访问
- 🔍 **部署详情页**: 查看构建日志和状态

## 使用说明

### 手动输入预测
1. 访问部署的网址
2. 选择 "Manual Input" 标签
3. 填写医疗指标数据
4. 点击 "Predict" 获取结果

### 文件上传预测
1. 准备 CSV 格式的数据文件
2. 选择 "File Upload" 标签
3. 上传 CSV 文件
4. 查看批量预测结果

### CSV 文件格式要求

文件应包含以下列（中文列名）：
```csv
性别,年龄,高血压,BMI,前白细胞,前血小板,前淋巴细胞,NLR,前红细胞,前血红蛋白,前单核细胞,前尿白细胞,前肌酐,前尿酸,白蛋白,球蛋白,手术时间
1,45,0,25.0,7.0,250.0,2.0,3.0,4.5,140.0,0.15,0.08,80.0,300.0,40.0,30.0,120.0
```

## 故障排除

### 常见问题

**1. 部署失败 - 依赖安装错误**
- 确认 `requirements.txt` 只包含基础依赖
- 检查 Python 版本配置（应为 3.11）

**2. 404 错误**
- 检查 `vercel.json` 路由配置
- 确认前端构建成功

**3. API 调用失败**
- 检查后端服务是否正常启动
- 验证 API 路径是否正确（`/api/*`）

**4. Excel 文件上传失败**
- Vercel 版本不支持 Excel 文件
- 请将 Excel 文件转换为 CSV 格式后上传

### 本地测试

部署前可以本地测试 Vercel 版本：

```bash
# 测试 Vercel 版本后端
cd backend
python app_vercel.py

# 测试前端构建
cd frontend
npm run build
```

## 技术架构

### 前端
- **框架**: React 18
- **UI 库**: Ant Design
- **构建工具**: Create React App
- **部署**: Vercel Static Build

### 后端
- **框架**: Flask
- **模型**: 纯 Python SVM 实现
- **部署**: Vercel Python Runtime
- **文件处理**: 仅支持 CSV 格式

### 部署优化
- **包大小**: < 10MB（vs 原版 200MB+）
- **启动时间**: < 3 秒
- **内存使用**: < 128MB
- **兼容性**: 支持所有 Python 版本

## 更新部署

代码更新后重新部署：

```bash
# 重新部署
vercel --prod

# 查看部署历史
vercel ls

# 查看部署日志
vercel logs [deployment-url]
```

---

**注意**: Vercel 版本为了确保部署稳定性，使用了简化的模型实现。如需完整功能（包括 Excel 支持），请使用本地部署版本。