from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os

from scipy.linalg import pinvh
from sklearn.preprocessing import StandardScaler
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 定义特征列（根据您的model.py）
CATEGORICAL_FEATURES = ['性别', '糖尿病史', '高血压', '前亚硝酸盐', 'ASA', '结石位置']
NUMERICAL_FEATURES = ['年龄', '身高', '体重', 'BMI', '前白细胞', '前中性粒', '前血小板', 
                     '前淋巴细胞', 'NLR', 'PLR', 'LMR', '前红细胞', '前血红蛋白',
                     '前单核细胞', '前尿白细胞', '前肌酐', '前尿素', '前尿酸', 
                     '总蛋白', '白蛋白', '球蛋白', '白球比', '手术时间']

# 加载模型和预处理器
model = None
scaler = None
selected_features = ['性别', '年龄', '高血压', 'BMI', '前白细胞', '前血小板', '前淋巴细胞', 'NLR', '前红细胞', '前血红蛋白', '前单核细胞', '前尿白细胞', '前肌酐', '前尿酸', '白蛋白', '球蛋白', '手术时间']

def load_model():
    """加载训练好的模型"""
    global model, scaler
    try:
        # 加载SVM模型
        model = joblib.load('svm_model.pkl')
        logger.info("SVM模型加载成功")
        
        # 创建标准化器（这里需要根据您的训练数据重新拟合）
        scaler = StandardScaler()
        
        # 读取原始数据来拟合标准化器
        if os.path.exists('original_data_samples.xlsx'):
            df = pd.read_excel('original_data_samples.xlsx')
            numeric_cols = [col for col in NUMERICAL_FEATURES if col in df.columns]
            df = pd.get_dummies(df, columns=CATEGORICAL_FEATURES)
            scaler.fit(df[numeric_cols])
            logger.info("标准化器拟合成功")

        return True
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False

def preprocess_data(data):
    """预处理数据"""
    try:
        # 处理分类变量 - 使用one-hot编码
        categorical_data = data[CATEGORICAL_FEATURES].copy()
        # categorical_dummies = pd.get_dummies(categorical_data, columns=CATEGORICAL_FEATURES)

        # 处理数值变量
        numerical_data = data[NUMERICAL_FEATURES].copy()
        
        # 处理缺失值
        numerical_data = numerical_data.fillna(numerical_data.median())
        categorical_dummies = categorical_data.fillna(0)
        
        # 标准化数值特征
        if scaler is not None:
            numerical_data = pd.DataFrame(
                scaler.transform(numerical_data), 
                columns=NUMERICAL_FEATURES,
                index=numerical_data.index
            )

        # 合并特征
        processed_data = pd.concat([numerical_data, categorical_dummies], axis=1)
        # print(processed_data)
        # 确保所有必要的特征都存在
        for feature in selected_features:
            if feature not in processed_data.columns:
                processed_data[feature] = 0
        
        # 只选择模型训练时使用的特征
        if selected_features:
            available_features = [f for f in selected_features if f in processed_data.columns]
            processed_data = processed_data[available_features]
        
        return processed_data
    except Exception as e:
        logger.error(f"数据预处理失败: {e}")
        raise e

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'message': 'SVM预测服务运行正常'})

@app.route('/api/predict', methods=['POST'])
def predict():
    """预测端点"""
    try:
        if model is None or selected_features is None:
            if not load_model():
                return jsonify({'error': '模型未加载'}), 500

        if request.is_json:
            # JSON数据
            data = request.get_json()
            if 'data' not in data:
                return jsonify({'error': '缺少数据字段'}), 400
            # 转换为DataFrame
            df = pd.DataFrame(data['data'])
        else:
            # 文件上传
            if 'file' not in request.files:
                return jsonify({'error': '没有文件上传'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '没有选择文件'}), 400
            # 读取文件
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return jsonify({'error': '不支持的文件格式，请上传CSV或Excel文件'}), 400
        # 检查必要的列
        required_columns = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
        missing_columns = [col for col in required_columns if col not in list(df.columns)]
        if isinstance(missing_columns, list) and len(missing_columns) > 0:
            return jsonify({
                'error': f'缺少必要的列: {missing_columns}',
                'required_columns': required_columns
            }), 400
        # logger.info(f"model: {model}")
        # logger.info(f"selected_features: {selected_features}")
        # logger.info(f"df columns: {df.columns}")
        # 预处理
        df_processed = preprocess_data(df[required_columns].copy())
        logger.info(f"df_processed columns: {df_processed.columns}")
        
        # 预测
        if model is None:
            if not load_model():
                return jsonify({'error': '模型未加载'}), 500
        
        predictions = model.predict(df_processed)
        probabilities = model.predict_proba(df_processed) if hasattr(model, 'predict_proba') else None
        
        # 准备结果
        results = []
        for i, pred in enumerate(predictions):
            result = {
                'row': i + 1,
                'prediction': int(pred),
                'prediction_label': '阳性' if pred == 1 else '阴性'
            }
            if probabilities is not None:
                result['confidence'] = float(max(probabilities[i]))
                result['probabilities'] = {
                    'negative': float(probabilities[i][0]),
                    'positive': float(probabilities[i][1])
                }
            results.append(result)
        
        return jsonify({
            'success': True,
            'predictions': results,
            'total_samples': len(results)
        })
        
    except Exception as e:
        logger.error(f"预测失败: {e}")
        return jsonify({'error': f'预测失败: {str(e)}'}), 500

@app.route('/api/features', methods=['GET'])
def get_features():
    """获取特征信息"""
    return jsonify({
        'categorical_features': CATEGORICAL_FEATURES,
        'numerical_features': NUMERICAL_FEATURES,
        'all_features': CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    })

@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """获取模型信息"""
    try:
        if model is None:
            return jsonify({'error': '模型未加载'}), 500
        
        return jsonify({
            'model_type': 'SVM',
            'features_count': len(selected_features) if selected_features else 0,
            'selected_features': selected_features[:10] if selected_features else []  # 只显示前10个特征
        })
    except Exception as e:
        return jsonify({'error': f'获取模型信息失败: {str(e)}'}), 500

if __name__ == '__main__':
    # 启动时加载模型
    if load_model():
        logger.info("系统启动成功，模型已加载")
    else:
        logger.error("系统启动失败，模型加载失败")
    app.run(debug=True, host='0.0.0.0', port=5001)
