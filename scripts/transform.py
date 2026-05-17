import duckdb
import pandas as pd
import os

# path dinamis
if os.path.exists("/opt/airflow"):
    BASE_DIR = "/opt/airflow"  # untuk airflow
else:
    BASE_DIR = "D:/REYHAN/BOOST ACADEMY/projek_akhir"  # untuk lokal

database_path = f"{BASE_DIR}/duckdb/dev.duckdb"
save_path_csv = f"{BASE_DIR}/prod_analysis.csv"

'''
load semua tabel yang sudah masuk ke duck lake
'''
try:
    con = duckdb.connect(database_path, read_only = False)
    print(f"✅ Berhasil terhubung ke database DuckDB di {database_path}.")

    tables = ['orders', 'order_items', 'products', 'users', 'inventory_items', 'events']
    dfs = {}

    for table in tables:
        query = f"SELECT * FROM raw_{table}"
        dfs[table] = con.execute(query).df()
        print(f"✅ Dataframe {table} telah siap.")


    #----------------- ATRIBUT TOTAL ORDER
    '''
    definisikan total order pada dataframe users
    '''
    df_orders2 = dfs['orders'].copy()
    df_orders2 = df_orders2[df_orders2['status'] != 'Cancelled']
    retensi_user = df_orders2.groupby('user_id')['order_id'].count().reset_index()
    retensi_user = retensi_user.rename(columns= {'order_id':'total_order'})
    df_customer = pd.merge(
        dfs['users'], retensi_user, left_on='id', right_on='user_id'
        ).drop(columns=['user_id'])


    #----------------- TARGET CUSTOMER CHURN
    '''
    definisikan target customer churn pada dataframe users
    '''
    df_last_purchase = df_orders2.groupby('user_id')['created_at'].max().reset_index()
    df_last_purchase = df_last_purchase.rename(columns= {'created_at':'last_order_date'}) 
    date_terbaru = df_orders2['created_at'].max()
    print(f"Last order date (Today): {date_terbaru}")

    df_customer2 = pd.merge(
        df_customer, df_last_purchase, 
        left_on='id', 
        right_on='user_id',
        how='left'
    ).drop(columns=['user_id'])

    # selisih hari last order dengan akun dibuat
    df_customer2['date_diff'] = (date_terbaru - df_customer2['last_order_date']).dt.days


    '''
    treshold target churn adalah 180 hari sebagai batas toleransi.
    jika tidak belanja > 180 hari maka label=1, jika masih aktif belanja label=0
    '''
    treshold_days = 180
    df_customer2['is_churn'] = ((df_customer2['date_diff'] > 180) | (df_customer2['date_diff'].isna())).astype(int)
    print(f"Presentase: {df_customer2['is_churn'].value_counts(normalize=True)*100}")



    #----------------- ATRIBUT CUSTOMER SPEND
    df_size = dfs['order_items'].groupby('user_id')['sale_price'].sum().reset_index()
    df_size = df_size.rename(columns= {'sale_price':'total_spend'})
    df_prafinal = pd.merge(
        df_customer2, 
        df_size, 
        left_on='id', 
        right_on='user_id', 
        how='left'    
    ).drop(columns=['user_id'])

    df_prafinal['avg_order_value'] = df_prafinal['total_spend']/df_prafinal['total_order']



    #----------------- ATRIBUT CATEGORY PRODUCT
    df_cat_prod = dfs['order_items'].merge(
        dfs['products'][['id','category']],
        left_on='product_id',
        right_on='id',
        how='left'
    ).drop(columns=['id_y'])
    df_cat_prod = df_cat_prod.rename(columns={'id_x':'id'})
    cat_matrix = pd.crosstab(
        df_cat_prod['user_id'],df_cat_prod['category']
        ).add_prefix('cat_')
    cat_matrix['unique_category_count'] = (cat_matrix > 0).sum(axis=1)


    from function import clean_names
    cat_matrix = clean_names(cat_matrix).reset_index()
    # cat_pct = cat_matrix.div(cat_matrix.sum(axis=1), axis=0).reset_index()

    df_prafinal2 = pd.merge(
        df_prafinal, 
        cat_matrix[['user_id','unique_category_count']], 
        left_on='id',
        right_on='user_id',
        how='left'
    ).drop(columns=['user_id'])


    '''
    Final Dataframe:
    target (y): is_churn.
    atribut (X): age, gender, state, city, country, 
                traffic_source, last_order_date, date_diff, total_spend,
                category one hot encoding
    '''

    base_columns = [
        'id','age', 'gender', 'state', 'city', 'country', 'traffic_source', 
        'last_order_date', 'date_diff', 'total_order', 'total_spend',
        'avg_order_value','unique_category_count','is_churn'
    ]
    cat_columns = []
    # cat_columns = [col for col in df_prafinal2.columns if 
    #                col.startswith('cat_')]
    list_columns = base_columns + cat_columns

    df_final = df_prafinal2[list_columns]
    print("✅ Dataframe df_final sudah siap untuk modeling.")
    # df_final adalah dataframe yang sudah siap untuk proses modeling, dengan target is_churn dan atribut-atribut yang sudah dipilih.

    # simpan dataframe modelling ke duckdb
    con.execute("CREATE OR REPLACE TABLE analytics_cust_churn AS SELECT * FROM df_final")
    print("✅ Dataframe df_final berhasil disimpan ke DuckDB sebagai analytics_cust_churn.")



    # PRODUCT ANALYSIS DATAFRAME
    prod_country = pd.merge(
        dfs['order_items'], dfs['users'][['id','age','gender','city','country','latitude','longitude','traffic_source']],
        left_on='user_id', right_on='id', how='left'
    ).drop(columns=['id_y'])
    prod_country = prod_country.rename(columns={'id_x':'id'})

    prod_gab = pd.merge(
        prod_country, dfs['products'][['id','category','brand','name','department']],
        left_on='product_id', right_on='id', how='left'
    ).drop(columns=['id_y']) 
    prod_gab = prod_gab.rename(columns={'id_x':'id'})

    # simpan hasil analisis produk ke csv
    prod_gab.to_csv(save_path_csv, index=False)
    print(f"✅ Dataframe prod_gab untuk produk analisis dengan file prod_analysis.csv berhasil disimpan ke {save_path_csv}.")

except Exception as e:
    print(f"TERJADI KESALAHAN PADA TRANSFORMATION: {str(e)}")
    raise e