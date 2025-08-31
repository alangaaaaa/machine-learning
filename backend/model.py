import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import Lasso
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix)
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, RocCurveDisplay
import joblib
# 1. 数据准备
def load_and_preprocess(file_path):
    df = pd.read_excel(file_path)
    print(df)
    label_col = 'label'

    categorical_cols = ['性别', '糖尿病史', '高血压', '前亚硝酸盐', 'ASA', '结石位置']
    numeric_cols = ['年龄', '身高', '体重', 'BMI', '前白细胞', '前中性粒', '前血小板',
                    '前淋巴细胞', 'NLR', 'PLR', 'LMR', '前红细胞', '前血红蛋白',
                    '前单核细胞', '前尿白细胞', '前肌酐', '前尿素',
                    '前尿酸', '总蛋白', '白蛋白', '球蛋白', '白球比', '手术时间']

    df = pd.get_dummies(df, columns=categorical_cols)

    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    X = df.drop([label_col, 'num'], axis=1)
    y = df[label_col]

    return X, y


def lasso_feature_selection(X, y, alpha=0.01):
    lasso = Lasso(alpha=alpha)
    lasso.fit(X, y)

    selected_features = X.columns[lasso.coef_ != 0]
    return selected_features


# 3. 模型训练与评估（仅使用SVM）
def train_and_evaluate_svm(X, y, selected_features):
    X_train, X_test, y_train, y_test = train_test_split(
        X[selected_features], y, stratify=y, test_size=0.2, random_state=42, shuffle=True)

    # 仅使用SVM模型
    svm_model = SVC(probability=True, random_state=42)
    svm_model.fit(X_train, y_train)
    joblib.dump(svm_model, 'svm_model.pkl')
    # 预测
    y_pred = svm_model.predict(X_test)
    y_proba = svm_model.predict_proba(X_test)[:, 1]

    # 计算评估指标
    metrics = {
        'Model': 'SVM',
        'Test Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1 Score': f1_score(y_test, y_pred),
        'ROC AUC': roc_auc_score(y_test, y_proba)
    }

    return pd.DataFrame([metrics])


# 主函数
def main():
    file_path = "/Users/alang/PycharmProjects/PythonProject/original_data_samples.xlsx"
    X, y = load_and_preprocess(file_path)

    selected_features = lasso_feature_selection(X, y)
    print(f"Selected features: {selected_features.tolist()}")

    results = train_and_evaluate_svm(X, y, selected_features)
    print("\nModel Performance:")
    print(results)


if __name__ == "__main__":
    main()