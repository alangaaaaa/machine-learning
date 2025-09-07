#!/bin/bash

# 服务启动和监控脚本
# 确保前端和后端服务持续运行

echo "启动SVM医疗预测系统服务..."

# 创建日志目录
mkdir -p logs

# 函数：启动后端服务
start_backend() {
    echo "启动后端服务..."
    cd backend
    nohup python app.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    echo "后端服务已启动，PID: $BACKEND_PID"
    cd ..
}

# 函数：启动前端服务
start_frontend() {
    echo "启动前端服务..."
    cd frontend
    nohup npm start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    echo "前端服务已启动，PID: $FRONTEND_PID"
    cd ..
}

# 函数：检查服务状态
check_service() {
    local service_name=$1
    local pid_file=$2
    local port=$3
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "$service_name 正在运行 (PID: $pid)"
            return 0
        else
            echo "$service_name 进程已停止"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo "$service_name 未启动"
        return 1
    fi
}

# 函数：停止服务
stop_services() {
    echo "停止所有服务..."
    
    # 停止后端
    if [ -f "logs/backend.pid" ]; then
        local backend_pid=$(cat "logs/backend.pid")
        if ps -p $backend_pid > /dev/null 2>&1; then
            kill $backend_pid
            echo "后端服务已停止"
        fi
        rm -f "logs/backend.pid"
    fi
    
    # 停止前端
    if [ -f "logs/frontend.pid" ]; then
        local frontend_pid=$(cat "logs/frontend.pid")
        if ps -p $frontend_pid > /dev/null 2>&1; then
            kill $frontend_pid
            echo "前端服务已停止"
        fi
        rm -f "logs/frontend.pid"
    fi
}

# 函数：监控和自动重启
monitor_services() {
    echo "开始监控服务..."
    while true; do
        # 检查后端服务
        if ! check_service "后端服务" "logs/backend.pid" "5001"; then
            echo "重启后端服务..."
            start_backend
        fi
        
        # 检查前端服务
        if ! check_service "前端服务" "logs/frontend.pid" "3000"; then
            echo "重启前端服务..."
            start_frontend
        fi
        
        # 等待30秒后再次检查
        sleep 30
    done
}

# 处理命令行参数
case "$1" in
    start)
        echo "启动服务..."
        start_backend
        sleep 5
        start_frontend
        echo "所有服务已启动"
        echo "后端地址: http://localhost:5001"
        echo "前端地址: http://localhost:3000"
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_backend
        sleep 5
        start_frontend
        ;;
    status)
        check_service "后端服务" "logs/backend.pid" "5001"
        check_service "前端服务" "logs/frontend.pid" "3000"
        ;;
    monitor)
        monitor_services
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|monitor}"
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 检查服务状态"
        echo "  monitor - 启动监控模式（自动重启失败的服务）"
        exit 1
        ;;
esac