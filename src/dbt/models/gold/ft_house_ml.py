import os
import pickle
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


def model(dbt, session):
    """
    Gold Layer: ML用特徴量エンジニアリング
    仕様書に基づく高次特徴量の生成と前処理アーティファクトの保存
    """
    
    # Silverデータの取得
    silver_df = dbt.ref("silver_house_data")
    df = silver_df.df()
    
    # 品質フラグでフィルタリング（仕様書 2.3）
    df = df[df["is_complete_record"] == True].copy()
    df = df[df["is_price_outlier"] == False].copy()
    df = df[df["is_age_outlier"] == False].copy()
    
    print(f"Processing {len(df)} records for ML features")
    
    # 特徴量エンジニアリング（仕様書 3）
    df = _engineer_features(df)
    
    # エンコーディングとスケーリング（仕様書 4）
    df = _encode_and_scale_features(df)
    
    # アーティファクト保存（仕様書 5）
    _save_preprocessing_artifacts(df)
    
    return df


def _engineer_features(df):
    """特徴量エンジニアリング（仕様書 3）"""
    
    # 3.1 対数変換
    df["log_price"] = np.log1p(df["price"])
    df["log_sqft"] = np.log1p(df["sqft"])
    
    # 3.2 多項式特徴量
    df["sqft_squared"] = df["sqft"] ** 2
    df["price_per_sqft_squared"] = df["price_per_sqft"] ** 2
    df["sqft_cubed"] = df["sqft"] ** 3
    
    # 3.3 交互作用特徴量
    df["price_bedrooms_interaction"] = df["price"] * df["bedrooms"]
    df["price_bathrooms_interaction"] = df["price"] * df["bathrooms"]
    df["sqft_bedrooms_interaction"] = df["sqft"] * df["bedrooms"]
    df["sqft_bathrooms_interaction"] = df["sqft"] * df["bathrooms"]
    df["price_sqft_ratio"] = df["price"] / df["sqft"]
    
    # 3.4 カテゴリカル特徴量の作成
    df["is_old_house"] = (df["house_age"] > 50).astype(int)
    df["is_new_house"] = (df["house_age"] < 10).astype(int)
    df["is_medium_age"] = ((df["house_age"] >= 10) & (df["house_age"] <= 50)).astype(int)
    
    # 四分位ベースの特徴量
    sqft_q1, sqft_q3 = df["sqft"].quantile([0.25, 0.75])
    price_q1, price_q3 = df["price"].quantile([0.25, 0.75])
    
    df["is_small_house"] = (df["sqft"] < sqft_q1).astype(int)
    df["is_large_house"] = (df["sqft"] > sqft_q3).astype(int)
    df["is_affordable"] = (df["price"] < price_q1).astype(int)
    df["is_expensive"] = (df["price"] > price_q3).astype(int)
    
    # 3.5 位置ベース特徴量
    location_avg_price = df.groupby("location")["price"].mean()
    df["location_avg_price"] = df["location"].map(location_avg_price)
    df["price_vs_location_avg"] = df["price"] / df["location_avg_price"]
    
    # 位置別ランク
    df["location_price_rank"] = df.groupby("location")["price"].rank(pct=True)
    
    # 3.6 条件スコアの数値化
    condition_mapping = {"POOR": 1, "FAIR": 2, "GOOD": 3, "EXCELLENT": 4}
    df["condition_score"] = df["condition"].map(condition_mapping)
    
    return df


def _encode_and_scale_features(df):
    """エンコーディングとスケーリング（仕様書 4）"""
    
    # 4.2 ラベルエンコーディング
    le_location = LabelEncoder()
    df["location_encoded"] = le_location.fit_transform(df["location"])
    
    # 4.3 特徴量スケーリング
    scale_features = [
        "price", "sqft", "bedrooms", "bathrooms", "year_built",
        "price_per_sqft", "house_age", "bed_bath_ratio",
        "log_price", "log_sqft", "sqft_squared", "price_per_sqft_squared",
        "sqft_cubed", "price_bedrooms_interaction", "price_bathrooms_interaction",
        "sqft_bedrooms_interaction", "sqft_bathrooms_interaction",
        "location_avg_price", "price_vs_location_avg", "location_price_rank"
    ]
    
    # 存在する特徴量のみをスケーリング
    available_features = [f for f in scale_features if f in df.columns]
    
    if available_features:
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df[available_features])
        df_scaled = pd.DataFrame(
            df_scaled,
            columns=[f"{f}_scaled" for f in available_features],
            index=df.index
        )
        
        # スケール済み特徴量を追加
        df = pd.concat([df, df_scaled], axis=1)
        
        # スケーラーを保存
        _save_artifact(scaler, "feature_scaler.pkl")
    
    # ラベルエンコーダーを保存
    _save_artifact(le_location, "location_mapping.pkl")
    
    return df


def _save_preprocessing_artifacts(df):
    """前処理アーティファクトの保存（仕様書 5）"""
    # アーティファクト保存ディレクトリの作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifacts_dir = Path(f"target/preprocessing_artifacts/{timestamp}")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 5.1 特徴量名リスト
    feature_names = [col for col in df.columns if col != "price"]
    _save_artifact(feature_names, "feature_names.pkl", artifacts_dir)

    # 5.2 データ統計情報（数値カラムのみ）
    numeric_df = df.select_dtypes(include=[np.number])
    stats = {
        "mean": numeric_df.mean().to_dict(),
        "std": numeric_df.std().to_dict(),
        "min": numeric_df.min().to_dict(),
        "max": numeric_df.max().to_dict(),
        "median": numeric_df.median().to_dict()
    }
    _save_artifact(stats, "data_stats.pkl", artifacts_dir)

    # 5.3 条件マッピング
    condition_mapping = {"POOR": 1, "FAIR": 2, "GOOD": 3, "EXCELLENT": 4}
    _save_artifact(condition_mapping, "condition_mapping.pkl", artifacts_dir)

    print(f"Preprocessing artifacts saved to {artifacts_dir}")


def _save_artifact(obj, filename, artifacts_dir=None):
    """アーティファクト保存のヘルパー関数"""
    if artifacts_dir is None:
        artifacts_dir = Path("target/preprocessing_artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    with open(artifacts_dir / filename, "wb") as f:
        pickle.dump(obj, f) 