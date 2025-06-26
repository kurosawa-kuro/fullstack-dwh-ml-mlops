# 設定ファイル構成

このディレクトリには、House Price Predictorアプリケーションの設定ファイルが含まれています。

## ファイル構成

### 基本設定
- **`base.yaml`** - 共通設定（プロジェクト情報、データ設定、データベース設定など）
- **`app.yaml`** - アプリケーション固有設定（MLflow設定など）

### 機能別設定
- **`training.yaml`** - モデル訓練設定（データ分割、交差検証、ハイパーパラメータ最適化など）
- **`model.yaml`** - モデル設定（特徴量、ベースモデル、評価設定など）
- **`ensemble.yaml`** - アンサンブルモデル設定（アンサンブル方法、ベースモデル、重み設定など）

### 依存関係
- **`requirements.txt`** - Python依存関係

## 設定の階層構造

```
configs/
├── base.yaml          # 共通設定（最優先）
├── app.yaml           # アプリケーション設定
├── training.yaml      # 訓練設定
├── model.yaml         # モデル設定
├── ensemble.yaml      # アンサンブル設定
├── requirements.txt   # 依存関係
└── README.md         # このファイル
```

## 設定の読み込み順序

1. `base.yaml` - 基本設定を読み込み
2. `app.yaml` - アプリケーション固有設定で上書き
3. 機能別設定ファイル - 必要に応じて読み込み

## 主要な設定項目

### プロジェクト設定
- プロジェクト名、バージョン、環境情報
- Python バージョン、依存関係

### データ設定
- 生データ、処理済みデータ、特徴量データのパス
- データベース接続設定（DuckDB）

### 機械学習設定
- 特徴量設定（数値、カテゴリカル）
- モデル設定（RandomForest、XGBoost、GradientBoosting）
- 評価メトリクス（MAE、R²、RMSE、MAPE）

### MLflow設定
- 実験管理、モデルレジストリ
- アーティファクト保存、ログ設定

### パフォーマンス設定
- 並列処理、メモリ管理
- バッチサイズ、キャッシュ設定

## 使用方法

### Pythonでの設定読み込み例

```python
import yaml
from pathlib import Path

def load_config():
    config_dir = Path("configs")
    
    # 基本設定を読み込み
    with open(config_dir / "base.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # アプリケーション設定で上書き
    with open(config_dir / "app.yaml", "r", encoding="utf-8") as f:
        app_config = yaml.safe_load(f)
        config.update(app_config)
    
    # 必要に応じて機能別設定を読み込み
    with open(config_dir / "model.yaml", "r", encoding="utf-8") as f:
        model_config = yaml.safe_load(f)
        config["model"] = model_config
    
    return config

# 設定を使用
config = load_config()
print(f"Project: {config['project']['name']}")
print(f"Database: {config['database']['path']}")
```

### 環境変数での上書き

設定値は環境変数で上書きできます：

```bash
export HOUSE_PRICE_DEBUG=true
export HOUSE_PRICE_PORT=8080
export MLFLOW_TRACKING_URI=http://localhost:5000
```

## 設定の変更

### 新しい設定を追加する場合

1. 適切な設定ファイルを選択
2. YAML形式で設定を追加
3. コメントで説明を記載
4. 必要に応じてREADMEを更新

### 設定の検証

設定ファイルの構文を検証するには：

```bash
python -c "import yaml; yaml.safe_load(open('configs/base.yaml'))"
```

## 注意事項

- 設定ファイルはUTF-8エンコーディングで保存
- 機密情報（APIキー、パスワード）は環境変数で管理
- 設定変更後はアプリケーションの再起動が必要
- 本番環境では設定のバックアップを推奨 