import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from lightgbm import LGBMClassifier
# from sklearn.naive_bayes import GaussianNB
# from pycaret.classification import setup, compare_models, pull, evaluate_model, predict_model, save_model
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, precision_recall_curve, accuracy_score
import numpy as np
import joblib
import os
import duckdb


# Path dinamis
if os.path.exists("/opt/airflow"):
    BASE_DIR = "/opt/airflow"  # untuk airflow
else:
    BASE_DIR = "D:/REYHAN/BOOST ACADEMY/projek_akhir"  # untuk lokal

database_path = f"{BASE_DIR}/duckdb/dev.duckdb"
path_compare = f"{BASE_DIR}/multipage_app/prod_analysis.csv"
save_path_results = f"{BASE_DIR}/multipage_app/model_results.csv"
path_model = f"{BASE_DIR}/multipage_app/model.pkl"
path_le = f"{BASE_DIR}/multipage_app/label_encoder.pkl"


from function import show_outliers
try:
    con = duckdb.connect(database_path, read_only = True)
    df_final = con.execute("SELECT * FROM analytics_cust_churn").df()
    print("Data analytics_cust_churn berhasil dimuat dari DuckDB.")
except Exception as e:
    print(f"❌ Gagal memuat data dari DuckDB: {e}")
    raise e
con.close()


# Cleaning & outlier
missing_data = df_final.isnull().sum()
numeric_cols = df_final.select_dtypes(include=['number']).columns
numeric_cols = numeric_cols.drop(['id'])

for col in numeric_cols:
    print(f"=== Outlier Analysis for: {col} ===")
    show_outliers(df_final, col)
    print("\n" + "="*30 + "\n")

# # Aplikasikan metode machine learning dengan pycaret  
# df_compare = df_final.copy()
# drop_cols = ['id', 'last_order_date', 'date_diff']
# df_compare = df_compare.drop(columns=[c for c in drop_cols if c in df_compare.columns])

# s = setup(
#     data=df_compare, 
#     target='is_churn', 
#     session_id=42,
#     fix_imbalance=True, 
#     categorical_features=['gender', 'state', 'city', 'country', 'traffic_source'],
#     verbose=True
# )

# print("\nMembandingkan semua model... Mohon tunggu.")
# best_model = compare_models(sort='Recall')

# path_compare = "../multipage_app/best_model.csv"
# compare_result = pull()
# compare_result.to_csv(path_compare)

# korelasi
# corr_matrix = df_final.select_dtypes(include=["number"]).corr(method='spearman')
# plt.figure(figsize=(10, 7))
# sns.heatmap(
#     corr_matrix, 
#     annot=True,           # Tampilkan angka
#     fmt=".2f",            # Dua angka di belakang koma
#     cmap="coolwarm", 
#     linewidths=0.5,       # Beri jarak antar kotak agar tidak menempel
#     annot_kws={"size": 15}, # Perkecil ukuran font angka di dalam kotak
#     cbar_kws={"shrink": .15} # Perkecil ukuran batang warna (colorbar)
# )
# plt.xticks(rotation=45, ha='right', fontsize=15)
# plt.yticks(fontsize=15)

# plt.title("Correlation Matrix Customer Churn", fontsize=20)
# plt.tight_layout() # Memastikan tidak ada label yang terpotong di pinggir
# plt.show()



'''
Dari performa model menggunakan pycaret diperoleh
model terbaik adalah dengan Light Gradient Boosting Machine
'''
print("\n--- Memulai proses modeling dengan LightGBM Classifier ---")
df_model = df_final.copy()

# hapus kolom yang tidak diperlukan untuk modeling
drop_cols = ['id','last_order_date','date_diff']
df_model = df_model.drop(columns=drop_cols)

# label encoding untuk kolom kategorikal
le_dict = {}
cat_cols = ['gender', 'state', 'city', 'country', 'traffic_source']

for col in cat_cols:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col].astype(str))
    le_dict[col] = le

# split data menjadi fitur (X) dan target (y)
X = df_model.drop(columns=['is_churn'])
y = df_model['is_churn']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# LGBM training
lgbm_model = LGBMClassifier(
    n_estimators=100,
    learning_rate=0.05,
    is_unbalance=True,  # Penting untuk menangani data imbalance
    random_state=42,
    n_jobs=-1,
    verbose=-1
)
lgbm_model.fit(X_train, y_train)

# evaluasi model
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
    peluang = y_probs[idx]
    match = "✅" if asli == tebakan else "❌"
    print(f"  {asli}   |     {tebakan}     |     {peluang*100:6.2f}%     | {match}")


# Prediksi probabilitas untuk SELURUH data (X)
X_all_encoded = X.copy()

# Menampilkan hasil prediksi probabilitas dan kelas untuk seluruh data
df_final['y_prob'] = lgbm_model.predict_proba(X)[:, 1]
df_final['y_pred'] = lgbm_model.predict(X)

# Simpan hasil prediksi ke CSV sebagai bahan RAGs
df_final.to_csv(save_path_results, index=False)
print(f"✅ Hasil prediksi probabilitas dan kelas untuk seluruh data berhasil disimpan ke {save_path_results}.")


# Feature importance
importances = pd.Series(lgbm_model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\n--- Fitur Paling Berpengaruh ---")
print(importances.head(5))


# Simpan model dengan joblib
joblib.dump(lgbm_model, path_model)
joblib.dump(le_dict, path_le)
print(f"✅ Model LightGBM dan Label Encoders berhasil disimpan ke {path_model} dan {path_le}.")
print("✅ Proses modeling selesai dengan sukses!")



