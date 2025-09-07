from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from simple_model import SimpleSVMPredictor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 全局变量
model = None
selected_features = ['性别', '年龄', '高血压', 'BMI', '前白细胞', '前血小板', '前淋巴细胞', 'NLR', '前红细胞', '前血红蛋白', '前单核细胞', '前尿白细胞', '前肌酐', '前尿酸', '白蛋白', '球蛋白', '手术时间']

def load_model():
    """加载训练好的模型"""
    global model
    try:
        model = SimpleSVMPredictor()
        # 尝试加载原始模型文件，如果失败则使用默认参数
        model_path = 'svm_model.pkl'
        if os.path.exists(model_path):
            model.load_model(model_path)
        else:
            logger.warning("模型文件不存在，使用默认参数")
            model.load_model(None)
        
        logger.info("简化模型加载成功")
        return True
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False

def preprocess_data(data):
    """预处理数据"""
    try:
        # 创建特征向量
        feature_vector = []
        
        # 打印输入数据用于调试
        logger.info(f"预处理输入数据: {data}")
        
        for feature in selected_features:
            if feature in data:
                value = data[feature]
                if value is None or value == '':
                    value = 0
                feature_vector.append(float(value))
            else:
                # 如果找不到特征，记录并使用默认值
                logger.warning(f"找不到特征 {feature} 的匹配项")
                feature_vector.append(0.0)
        
        # 打印生成的特征向量用于调试
        logger.info(f"生成的特征向量: {feature_vector}")
        
        return feature_vector
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
        if not model:
            return jsonify({
                'success': False,
                'error': '模型未加载'
            }), 500

        # 处理 JSON 数据
        if request.is_json:
            data = request.get_json()
            
            # 预处理数据
            processed_data = preprocess_data(data)
            
            # 进行预测
            predictions, probabilities = model.predict(processed_data)
            prediction = int(predictions[0])
            probability = float(probabilities[0])
            
            # 计算置信度和概率分布
            confidence = max(probability, 1 - probability)
            
            result = {
                'prediction': prediction,
                'prediction_label': 'Positive' if prediction == 1 else 'Negative',
                'confidence': confidence,
                'probabilities': {
                    'negative': 1 - probability,
                    'positive': probability
                }
            }
            
            return jsonify({
                'success': True,
                'result': result
            })
        
        # 处理文件上传
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': '未选择文件'}), 400
            
            if not (file.filename.lower().endswith('.csv') or file.filename.lower().endswith('.xlsx') or file.filename.lower().endswith('.xls')):
                return jsonify({'success': False, 'error': '仅支持CSV和Excel文件'}), 400
            
            # 处理不同文件格式
            if file.filename.endswith('.csv'):
                # CSV文件处理
                content = file.read().decode('utf-8')
                lines = content.strip().split('\n')
                
                if len(lines) < 2:
                    return jsonify({'success': False, 'error': 'CSV文件格式错误'}), 400
                
                headers = [h.strip() for h in lines[0].split(',')]
                data_rows = []
                
                for i, line in enumerate(lines[1:], 1):
                    values = [v.strip() for v in line.split(',')]
                    if len(values) != len(headers):
                        continue
                    
                    # 创建数据字典
                    row_data = dict(zip(headers, values))
                    data_rows.append(row_data)
            
            elif file.filename.endswith(('.xlsx', '.xls')):
                # Excel文件处理
                try:
                    import pandas as pd
                    import io
                    
                    # 保存上传的文件到内存中
                    file_stream = io.BytesIO(file.read())
                    
                    # 使用pandas读取Excel文件
                    df = pd.read_excel(file_stream)
                    
                    # 打印列名用于调试
                    logger.info(f"Excel文件列名: {list(df.columns)}")
                    
                    # 检查是否包含所有必要的特征列
                    missing_features = [feature for feature in selected_features if feature not in df.columns]
                    if missing_features:
                        error_msg = f"Excel文件缺少必要的特征列: {', '.join(missing_features)}"
                        logger.error(error_msg)
                        return jsonify({'success': False, 'error': error_msg}), 400
                    
                    # 转换为字典列表
                    data_rows = df.to_dict('records')
                    
                    if len(data_rows) == 0:
                        return jsonify({'success': False, 'error': 'Excel文件为空'}), 400
                        
                    # 打印第一行数据用于调试
                    if data_rows:
                        logger.info(f"第一行数据: {data_rows[0]}")
                        logger.info(f"Excel第一行数据类型: {type(data_rows[0]).__name__}")
                        logger.info(f"Excel数据行数: {len(data_rows)}")
                    
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Excel文件处理错误: {str(e)}'}), 400
            
            else:
                return jsonify({'success': False, 'error': '仅支持CSV和Excel文件格式'}), 400
            
            # 批量预测
            results = []
            for i, row_data in enumerate(data_rows, 1):
                
                try:
                    # 预处理和预测
                    processed_data = preprocess_data(row_data)
                    predictions, probabilities = model.predict(processed_data)
                    prediction = int(predictions[0])
                    probability = float(probabilities[0])
                    
                    confidence = max(probability, 1 - probability)
                    
                    results.append({
                        'row': i,
                        'prediction': prediction,
                        'prediction_label': 'Positive' if prediction == 1 else 'Negative',
                        'confidence': confidence,
                        'probabilities': {
                            'negative': 1 - probability,
                            'positive': probability
                        }
                    })
                except Exception as e:
                    logger.error(f"处理第{i}行数据时出错: {e}")
                    continue
            
            return jsonify({
                'success': True,
                'total_samples': len(results),
                'predictions': results
            })
        
        else:
            return jsonify({'success': False, 'error': '无效的请求格式'}), 400
            
    except Exception as e:
        logger.error(f"预测过程中出错: {e}")
        return jsonify({
            'success': False,
            'error': f'预测失败: {str(e)}'
        }), 500

@app.route('/api/features', methods=['GET'])
def get_features():
    """获取特征列表"""
    return jsonify({
        'features': selected_features,
        'total_features': len(selected_features)
    })

@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """获取模型信息"""
    return jsonify({
        'model_type': 'Simplified SVM',
        'features_count': len(selected_features),
        'model_loaded': model is not None,
        'version': '1.0.0'
    })

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

# 初始化模型
if load_model():
    logger.info("系统启动成功，模型已加载")
else:
    logger.error("系统启动失败，模型加载失败")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)