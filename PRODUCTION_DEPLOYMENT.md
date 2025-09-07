# 生产环境部署指南

本文档提供了多种方式来确保SVM医疗预测系统在生产环境中持续稳定运行。

## 🚀 快速启动

### 方法1: 使用启动脚本（推荐用于开发/测试）

```bash
# 启动所有服务
./start_services.sh start

# 检查服务状态
./start_services.sh status

# 启动监控模式（自动重启失败的服务）
./start_services.sh monitor

# 停止所有服务
./start_services.sh stop
```

### 方法2: 使用Docker Compose（推荐用于生产环境）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方法3: 使用系统服务（Linux生产环境）

```bash
# 复制服务文件到系统目录
sudo cp svm-prediction.service /etc/systemd/system/

# 重载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable svm-prediction

# 启动服务
sudo systemctl start svm-prediction

# 查看服务状态
sudo systemctl status svm-prediction
```

## 🔧 配置说明

### 环境变量

- `NODE_ENV`: 前端环境（development/production）
- `FLASK_ENV`: 后端环境（development/production）
- `REACT_APP_API_URL`: 前端API地址配置

### 端口配置

- 前端服务: `3000`
- 后端服务: `5001`
- Nginx代理: `80` (HTTP), `443` (HTTPS)

## 📊 监控和日志

### 日志文件位置

```
logs/
├── backend.log          # 后端服务日志
├── frontend.log         # 前端服务日志
├── service.log          # 系统服务日志
├── service-error.log    # 系统服务错误日志
└── nginx/               # Nginx日志目录
    ├── access.log
    └── error.log
```

### 健康检查端点

- 后端健康检查: `http://localhost:5001/api/health`
- 前端健康检查: `http://localhost:3000`
- Nginx健康检查: `http://localhost/health`

## 🛠️ 故障排除

### 常见问题

1. **网络连接错误**
   ```bash
   # 检查服务是否运行
   ./start_services.sh status
   
   # 检查端口占用
   lsof -i :3000
   lsof -i :5001
   ```

2. **服务启动失败**
   ```bash
   # 查看详细日志
   tail -f logs/backend.log
   tail -f logs/frontend.log
   ```

3. **依赖问题**
   ```bash
   # 重新安装依赖
   cd backend && pip install -r requirements.txt
   cd frontend && npm install
   ```

### 自动重启机制

- **启动脚本**: 使用 `monitor` 模式每30秒检查服务状态
- **Docker**: 配置了 `restart: unless-stopped` 策略
- **系统服务**: 配置了 `Restart=always` 和 `RestartSec=10`

## 🔒 安全建议

1. **防火墙配置**
   ```bash
   # 只开放必要端口
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **SSL/TLS配置**
   - 在生产环境中配置HTTPS
   - 使用Let's Encrypt获取免费SSL证书

3. **访问控制**
   - 配置Nginx访问限制
   - 使用反向代理隐藏内部服务

## 📈 性能优化

1. **资源限制**
   ```yaml
   # Docker Compose中添加资源限制
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

2. **缓存配置**
   - 配置Nginx静态文件缓存
   - 使用Redis缓存预测结果（可选）

3. **负载均衡**
   - 多实例部署
   - 使用Nginx upstream配置

## 🚀 云平台部署

### Vercel部署
```bash
# 使用现有的Vercel配置
./deploy_vercel.sh
```

### AWS/Azure/GCP部署
- 使用Docker镜像部署到容器服务
- 配置负载均衡器和自动扩缩容
- 使用托管数据库服务

## 📞 支持

如果遇到问题，请检查：
1. 服务日志文件
2. 系统资源使用情况
3. 网络连接状态
4. 依赖版本兼容性