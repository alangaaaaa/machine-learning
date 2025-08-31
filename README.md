# SVM医疗预测系统

基于支持向量机(SVM)的医疗预测系统，支持本地表格文件上传和实时预测。

## 功能特性

- 🏥 **医疗预测**: 使用SVM机器学习模型进行医疗数据预测
- 📊 **文件上传**: 支持CSV和Excel文件格式
- 🔄 **实时预测**: 点击按钮即可获得预测结果
- 📈 **结果展示**: 清晰展示预测结果、置信度和概率
- 🎨 **现代UI**: 基于Ant Design的美观界面
- 📱 **响应式设计**: 支持桌面和移动设备

## 技术栈

### 后端
- **Flask**: Python Web框架
- **scikit-learn**: 机器学习库
- **pandas**: 数据处理
- **Vercel**: 部署平台

### 前端
- **React**: 前端框架
- **Ant Design**: UI组件库
- **Axios**: HTTP客户端

## 特征变量

### 分类变量
- 性别
- 糖尿病史
- 高血压
- 前亚硝酸盐
- ASA
- 结石位置

### 连续变量
- 年龄、身高、体重、BMI
- 前白细胞、前中性粒、前血小板
- 前淋巴细胞、NLR、PLR、LMR
- 前红细胞、前血红蛋白、前单核细胞
- 前尿白细胞、前肌酐、前尿素、前尿酸
- 总蛋白、白蛋白、球蛋白、白球比
- 手术时间

## 快速开始

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd svm-medical-prediction
```

2. **启动后端服务**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

3. **启动前端服务**
```bash
cd frontend
npm install
npm start
```

4. **访问应用**
打开浏览器访问 `http://localhost:3000`

### 部署到Vercel

1. **部署后端**
```bash
cd backend
vercel
```

2. **部署前端**
```bash
cd frontend
npm run build
vercel --prod
```

3. **配置环境变量**
在Vercel控制台设置 `REACT_APP_API_URL` 为后端API地址

## API接口

### 健康检查
```
GET /api/health
```

### 预测接口
```
POST /api/predict
Content-Type: multipart/form-data
```

### 特征信息
```
GET /api/features
```

### 模型上传
```
POST /api/upload-model
Content-Type: multipart/form-data
```

## 使用说明

1. **准备数据文件**
   - 确保CSV或Excel文件包含所有必需的特征列
   - 数据格式应与示例文件一致

2. **上传文件**
   - 点击"选择CSV或Excel文件"按钮
   - 选择包含医疗数据的文件

3. **开始预测**
   - 点击"开始预测"按钮
   - 等待处理完成

4. **查看结果**
   - 在表格中查看预测结果
   - 包含预测标签、置信度和概率信息

## 项目结构

```
svm-medical-prediction/
├── backend/
│   ├── app.py              # Flask主应用
│   ├── requirements.txt    # Python依赖
│   └── vercel.json         # Vercel配置
├── frontend/
│   ├── src/
│   │   ├── App.js          # 主组件
│   │   └── App.css         # 样式文件
│   ├── package.json        # Node.js依赖
│   └── public/             # 静态文件
├── sample_data.csv         # 示例数据
└── README.md              # 项目说明
```

## 注意事项

- 确保上传的数据文件包含所有必需的特征列
- 分类变量应使用中文标签（如：男/女、有/无等）
- 数值变量应为数字格式
- 系统会自动处理缺失值

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
