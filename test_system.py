#!/usr/bin/env python3
"""
SVM医疗预测系统测试脚本
"""

import requests
import json
import pandas as pd
import time

# 配置
BACKEND_URL = "http://localhost:5001"
SAMPLE_DATA_PATH = "sample_data.csv"

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

def test_features_api():
    """测试特征信息接口"""
    print("\n🔍 测试特征信息接口...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/features")
        if response.status_code == 200:
            print("✅ 特征信息获取成功")
            data = response.json()
            print(f"   分类特征: {len(data['categorical_features'])} 个")
            print(f"   数值特征: {len(data['numerical_features'])} 个")
        else:
            print(f"❌ 特征信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 特征信息获取异常: {e}")

def test_prediction_api():
    """测试预测接口"""
    print("\n🔍 测试预测接口...")
    try:
        # 读取示例数据
        df = pd.read_csv(SAMPLE_DATA_PATH)
        print(f"   加载了 {len(df)} 个样本")
        
        # 准备文件上传
        files = {'file': open(SAMPLE_DATA_PATH, 'rb')}
        
        # 发送预测请求
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/api/predict", files=files)
        end_time = time.time()
        
        if response.status_code == 200:
            print("✅ 预测成功")
            data = response.json()
            print(f"   处理时间: {end_time - start_time:.2f} 秒")
            print(f"   预测样本数: {data['total_samples']}")
            
            # 显示前几个预测结果
            predictions = data['predictions']
            print("   前3个预测结果:")
            for i, pred in enumerate(predictions[:3]):
                print(f"     样本{i+1}: {pred['prediction_label']} (置信度: {pred.get('confidence', 'N/A')})")
                
        else:
            print(f"❌ 预测失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 预测测试异常: {e}")

def test_invalid_file():
    """测试无效文件上传"""
    print("\n🔍 测试无效文件上传...")
    try:
        # 创建一个无效的CSV文件
        invalid_data = "invalid,columns\n1,2,3"
        with open("invalid.csv", "w") as f:
            f.write(invalid_data)
        
        files = {'file': open("invalid.csv", 'rb')}
        response = requests.post(f"{BACKEND_URL}/api/predict", files=files)
        
        if response.status_code == 400:
            print("✅ 无效文件处理正确")
            print(f"   错误信息: {response.json()['error']}")
        else:
            print(f"❌ 无效文件处理异常: {response.status_code}")
            
        # 清理临时文件
        import os
        os.remove("invalid.csv")
        
    except Exception as e:
        print(f"❌ 无效文件测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试SVM医疗预测系统")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 运行测试
    test_health_check()
    test_features_api()
    test_prediction_api()
    test_invalid_file()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")

if __name__ == "__main__":
    main()
