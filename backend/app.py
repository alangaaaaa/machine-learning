from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os
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
        # 导入model.py中的模型相关函数
        from sklearn.preprocessing import StandardScaler
        
        # 加载SVM模型
        model_path = os.path.join(os.path.dirname(__file__), 'svm_model.pkl')
        logger.info(f"尝试加载模型文件: {model_path}")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"文件是否存在: {os.path.exists(model_path)}")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            logger.info("SVM模型加载成功")
        else:
            # 如果模型文件不存在，使用默认SVM模型
            from sklearn.svm import SVC
            model = SVC(probability=True)
            logger.warning(f"模型文件不存在: {model_path}，使用默认SVM模型")
        
        # 初始化标准化器
        scaler = StandardScaler()
        # 使用预设的均值和标准差初始化标准化器
        scaler.mean_ = np.array([0.5, 45.0, 0.3, 25.0, 7.0, 250.0, 2.0, 3.0, 4.5, 140.0, 0.15, 0.08, 80.0, 300.0, 40.0, 30.0, 120.0])
        scaler.scale_ = np.array([0.5, 15.0, 0.5, 5.0, 3.0, 100.0, 1.0, 2.0, 2.0, 20.0, 0.1, 0.05, 20.0, 100.0, 10.0, 10.0, 60.0])
        logger.info("标准化器初始化成功")

        return True
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False

def preprocess_data(data):
    """预处理数据"""
    try:
        # 创建特征向量，按照selected_features的顺序
        feature_vector = []
        
        for feature in selected_features:
            if feature in data:
                value = data[feature]
                # 处理缺失值
                if value is None or value == '':
                    value = 0
                feature_vector.append(float(value))
            else:
                # 如果特征不存在，使用0填充
                feature_vector.append(0.0)
        
        # 转换为numpy数组
        processed_data = np.array([feature_vector])
        
        # 应用标准化
        if scaler:
            try:
                processed_data = scaler.transform(processed_data)
            except Exception as e:
                logger.warning(f"使用StandardScaler转换失败: {e}，尝试手动标准化")
                # 如果StandardScaler转换失败，使用手动标准化
                if hasattr(scaler, 'mean_') and hasattr(scaler, 'scale_'):
                    processed_data = (processed_data - scaler.mean_) / scaler.scale_
        
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
        if model is None:
            if not load_model():
                return jsonify({'error': '模型未加载'}), 500

        if request.is_json:
            # JSON数据 - 单个样本预测
            data = request.get_json()
            processed_data = preprocess_data(data)
            
            # 预测
            predictions = model.predict(processed_data)
            probabilities = model.predict_proba(processed_data) if hasattr(model, 'predict_proba') else None
            
            # 准备结果
            pred = predictions[0]
            result = {
                'prediction': int(pred),
                'prediction_label': 'Positive' if pred == 1 else 'Negative'
            }
            
            if probabilities is not None:
                result['confidence'] = float(max(probabilities[0]))
                result['probabilities'] = {
                    'negative': float(probabilities[0][0]),
                    'positive': float(probabilities[0][1])
                }
            
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            # 文件上传 - 批量预测
            if 'file' not in request.files:
                return jsonify({'error': '没有文件上传'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '没有选择文件'}), 400
            
            # 读取文件内容
            try:
                import io
                import pandas as pd
                
                if file.filename.endswith('.csv'):
                    # CSV文件处理
                    file_content = file.read().decode('utf-8')
                    lines = file_content.strip().split('\n')
                    headers = lines[0].split(',')
                    data_rows = []
                    for line in lines[1:]:
                        values = line.split(',')
                        row_data = {headers[i].strip(): values[i].strip() for i in range(len(headers))}
                        data_rows.append(row_data)
                elif file.filename.endswith(('.xlsx', '.xls')):
                    # Excel文件处理
                    file.seek(0)  # 重置文件指针
                    df = pd.read_excel(file)
                    data_rows = df.to_dict('records')
                else:
                    return jsonify({'error': '支持CSV和Excel文件格式'}), 400
                
                # 批量预测
                results = []
                for i, row_data in enumerate(data_rows):
                    try:
                        processed_data = preprocess_data(row_data)
                        pred = model.predict(processed_data)[0]
                        prob = model.predict_proba(processed_data)[0] if hasattr(model, 'predict_proba') else None
                        
                        result = {
                            'row': i + 1,
                            'prediction': int(pred),
                            'prediction_label': 'Positive' if pred == 1 else 'Negative'
                        }
                        
                        if prob is not None:
                            result['confidence'] = float(max(prob))
                            result['probabilities'] = {
                                'negative': float(prob[0]),
                                'positive': float(prob[1])
                            }
                        
                        results.append(result)
                    except Exception as e:
                        logger.error(f"处理第{i+1}行数据时出错: {e}")
                        results.append({
                            'row': i + 1,
                            'error': f'处理失败: {str(e)}'
                        })
                
                return jsonify({
                    'success': True,
                    'predictions': results,
                    'total_samples': len(results)
                })
                
            except Exception as e:
                return jsonify({'error': f'文件读取失败: {str(e)}'}), 400
        
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

@app.route('/api/download-template', methods=['GET'])
def download_template():
    """下载模板文件"""
    try:
        import pandas as pd
        import io
        from flask import send_file
        
        # 创建一个包含所有特征的DataFrame
        template_data = {feature: [""] for feature in selected_features}
        df = pd.DataFrame(template_data)
        
        # 添加一行示例数据
        example_data = {
            '性别': 1,  # 1表示男性
            '年龄': 65,
            '高血压': 1,  # 1表示有
            'BMI': 24.5,
            '前白细胞': 6.5,
            '前血小板': 200,
            '前淋巴细胞': 1.8,
            'NLR': 2.5,
            '前红细胞': 4.5,
            '前血红蛋白': 140,
            '前单核细胞': 0.5,
            '前尿白细胞': 0,
            '前肌酐': 80,
            '前尿酸': 350,
            '白蛋白': 40,
            '球蛋白': 25,
            '手术时间': 120
        }
        
        # 确保示例数据中包含所有需要的特征
        for feature in selected_features:
            if feature not in example_data:
                example_data[feature] = 0
        
        # 添加示例数据行
        df.loc[1] = [example_data[feature] for feature in selected_features]
        
        # 创建一个BytesIO对象
        output = io.BytesIO()
        
        # 将DataFrame写入Excel文件
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Template')
            
            # 获取xlsxwriter工作簿和工作表对象
            workbook = writer.book
            worksheet = writer.sheets['Template']
            
            # 添加一些格式
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })
            
            # 写入列标题
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # 设置列宽
            worksheet.set_column(0, len(df.columns) - 1, 15)
        
        # 设置指针到开始
        output.seek(0)
        
        # 发送文件
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='prediction_template.xlsx'
        )
    except Exception as e:
        logger.error(f"生成模板文件时出错: {e}")
        return jsonify({
            'success': False,
            'error': f'生成模板文件失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 启动时加载模型
    if load_model():
        logger.info("系统启动成功，模型已加载")
    else:
        logger.error("系统启动失败，模型加载失败")
    app.run(debug=True, host='0.0.0.0', port=5001)
