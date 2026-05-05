import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier
from sklearn.naive_bayes import GaussianNB
from pycaret.classification import setup, compare_models, pull, evaluate_model, predict_model, save_model
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, precision_recall_curve, accuracy_score
import numpy as np
import joblib

# Cleaning & outlier
missing_data = df_final.isnull().sum()

from function import show_outliers
numeric_cols = df_final.select_dtypes(include=['number']).columns
numeric_cols = numeric_cols.drop(['id'])
for col in numeric_cols:
    print(f"=== Outlier Analysis for: {col} ===")
    show_outliers(df_final, col)
    print("\n" + "="*30 + "\n")

# Aplikasikan metode machine learning dengan pycaret  
df_compare = df_final.copy()
drop_cols = ['id', 'last_order_date', 'date_diff']
df_compare = df_compare.drop(columns=[c for c in drop_cols if c in df_compare.columns])

s = setup(
    data=df_compare, 
    target='is_churn', 
    session_id=42,
    fix_imbalance=True, 
    categorical_features=['gender', 'state', 'city', 'country', 'traffic_source'],
    verbose=True
)

print("\nMembandingkan semua model... Mohon tunggu.")
best_model = compare_models(sort='AUC')



# korelasi
corr_matrix = df_final.select_dtypes(include=["number"]).corr(method='spearman')
plt.figure(figsize=(10, 7))
sns.heatmap(
    corr_matrix, 
    annot=True,           # Tampilkan angka
    fmt=".2f",            # Dua angka di belakang koma
    cmap="coolwarm", 
    linewidths=0.5,       # Beri jarak antar kotak agar tidak menempel
    annot_kws={"size": 15}, # Perkecil ukuran font angka di dalam kotak
    cbar_kws={"shrink": .15} # Perkecil ukuran batang warna (colorbar)
)
plt.xticks(rotation=45, ha='right', fontsize=15)
plt.yticks(fontsize=15)

plt.title("Correlation Matrix Customer Churn", fontsize=20)
plt.tight_layout() # Memastikan tidak ada label yang terpotong di pinggir
plt.show()



'''
Dari performa model menggunakan pycaret diperoleh
model terbaik adalah dengan Light Gradient Boosting Machine
'''
df_model = df_final.copy()
drop_cols = ['id','last_order_date','date_diff']
df_model = df_model.drop(columns=drop_cols)

le_dict = {}
cat_cols = ['gender', 'state', 'city', 'country', 'traffic_source']

for col in cat_cols:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col].astype(str))
    le_dict[col] = le

X = df_model.drop(columns=['is_churn'])
y = df_model['is_churn']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# NAIVE BAYES
nb_model = GaussianNB()
nb_model.fit(X_train, y_train)
y_pred = nb_model.predict(X_test)
y_probs_all = nb_model.predict_proba(X_test)
y_prob = y_probs_all[:, 1]
print("--- Confusion Matrix ---")
print(confusion_matrix(y_test, y_pred))

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred))

auc_score = roc_auc_score(y_test, y_prob)
print(f"Skor ROC-AUC Naive Bayes: {auc_score:.4f}")



# LGBM
lgbm_model = LGBMClassifier(
    n_estimators=100,
    learning_rate=0.05,
    is_unbalance=True,  # Penting untuk menangani data imbalance
    random_state=42,
    n_jobs=-1
)

lgbm_model.fit(X_train, y_train)

y_pred = lgbm_model.predict(X_test)
y_probs = lgbm_model.predict_proba(X_test)[:, 1]

print("--- Hasil Evaluasi LightGBM Classifier ---")
print(classification_report(y_test, y_pred))
print(f"ROC-AUC Score: {roc_auc_score(y_test, y_probs):.4f}")

# print
np.random.seed(42) 
random_indices = np.random.choice(len(y_test), size=20, replace=False)
print(" Asli |  Tebakan  |  Peluang Churn  | Match")
print("-" * 45)
for idx in random_indices:
    asli = y_test.iloc[idx] if hasattr(y_test, 'iloc') else y_test[idx]
    tebakan = y_pred[idx]
    peluang = y_prob[idx]
    match = "✅" if asli == tebakan else "❌"
    print(f"  {asli}   |     {tebakan}     |     {peluang*100:6.2f}%     | {match}")

# feature importance
importances = pd.Series(et_model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\n--- Fitur Paling Berpengaruh ---")
print(importances.head(10))


# simpan model dengan joblib
path_model = "../multipage_app/model.pkl"
joblib.dump(lgbm_model, path_model)
path_le = "../multipage_app/label_encoder.pkl"
joblib.dump(le_dict, path_le)





