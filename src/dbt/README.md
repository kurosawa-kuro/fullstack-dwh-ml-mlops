# dbt データパイプライン

このdbtプロジェクトは、**データ処理パイプライン仕様書**に基づいて構築されたMedallion Architecture（メダリオン・アーキテクチャ）の実装です。

## アーキテクチャ概要

```
Bronze Layer (bronze_raw_house_data)
    ↓
Silver Layer (silver_house_data) - データクリーニング
    ↓
Gold Layer (ft_house_ml) - 特徴量エンジニアリング
```

## プロジェクト構造

```
src/dbt/
├── dbt_project.yml          # dbtプロジェクト設定
├── profiles.yml             # データベース接続設定
├── packages.yml             # 依存パッケージ
├── models/
│   ├── sources.yml          # ソース定義
│   ├── silver/
│   │   ├── silver_house_data.sql    # Silver Layer
│   │   └── silver_house_data.yml    # テスト定義
│   └── gold/
│       ├── ft_house_ml.py           # Gold Layer (Python)
│       └── ft_house_ml.yml          # テスト定義
├── run_dbt_pipeline.py      # 実行スクリプト
└── README.md                # このファイル
```

## 前提条件

1. **Python環境**: Python 3.8以上
2. **dbt**: `pip install dbt-core dbt-duckdb`
3. **DuckDB**: 既存の`house_price_dwh.duckdb`ファイル

## セットアップ

### 1. 依存関係のインストール

```bash
cd src/dbt
dbt deps
```

### 2. プロファイルの確認

`profiles.yml`でDuckDBファイルのパスが正しいことを確認してください：

```yaml
path: "../../data/interim/house_price_dwh.duckdb"
```

## 実行方法

### 自動実行（推奨）

```bash
cd src/dbt
python run_dbt_pipeline.py
```

### 手動実行

```bash
cd src/dbt

# 依存関係インストール
dbt deps

# Silver Layer実行
dbt run --select silver

# Silver Layerテスト
dbt test --select silver

# Gold Layer実行
dbt run --select gold

# Gold Layerテスト
dbt test --select gold

# ドキュメント生成
dbt docs generate
```

## 各レイヤーの詳細

### Silver Layer (`silver_house_data`)

**目的**: データクリーニングと標準化

**処理内容**:
- 基本データクリーニング（価格、面積、部屋数の妥当性チェック）
- 建設年の範囲チェック（1900年〜現在年）
- 文字列列の標準化（トリム、大文字化）
- 派生フィールド計算（平米単価、築年数、寝室・バス比率）
- 品質フラグ付与（完全レコード、外れ値フラグ）

**出力スキーマ**: `silver`

### Gold Layer (`ft_house_ml`)

**目的**: ML用特徴量エンジニアリング

**処理内容**:
- 対数変換（価格、面積）
- 多項式特徴量（2次、3次）
- 交互作用特徴量（価格×部屋数など）
- カテゴリカル特徴量（古い家、大きい家など）
- 位置ベース特徴量（地域平均価格、ランク）
- 条件スコアの数値化
- ラベルエンコーディング
- 特徴量スケーリング
- 前処理アーティファクト保存

**出力スキーマ**: `gold`

## 前処理アーティファクト

Gold Layer実行時に以下のアーティファクトが保存されます：

```
target/preprocessing_artifacts/YYYYMMDD_HHMMSS/
├── feature_names.pkl        # 特徴量名リスト
├── data_stats.pkl           # データ統計情報
├── location_mapping.pkl     # 位置エンコーダー
├── condition_mapping.pkl    # 条件マッピング
└── feature_scaler.pkl       # 特徴量スケーラー
```

## テスト

各レイヤーには以下のテストが定義されています：

- **not_null**: 必須列のNULLチェック
- **unique**: 主キーの重複チェック
- **accepted_range**: 数値範囲の妥当性チェック

## ドキュメント

```bash
dbt docs generate
dbt docs serve
```

ブラウザで`http://localhost:8080`にアクセスしてドキュメントを確認できます。

## トラブルシューティング

### よくある問題

1. **DuckDBファイルが見つからない**
   - `profiles.yml`のパスを確認
   - 相対パスが正しいことを確認

2. **Pythonモデルの依存関係エラー**
   - `pip install scikit-learn pandas numpy`を実行

3. **dbtパッケージエラー**
   - `dbt deps`を再実行

### ログの確認

```bash
# 詳細ログで実行
dbt run --select silver --debug

# ログファイルの確認
tail -f logs/dbt.log
```

## 仕様書との対応

このdbtプロジェクトは以下の仕様書セクションに対応しています：

- **1. Silver Layer**: データクリーニング
- **2. 外れ値処理**: 統計的・ドメイン知識ベース
- **3. Gold Layer**: 特徴量エンジニアリング
- **4. エンコーディング & スケーリング**: ラベルエンコーディング、StandardScaler
- **5. アーティファクト管理**: タイムスタンプ付き保存

## 貢献

このプロジェクトは仕様書に基づいて構築されています。変更を行う場合は、必ず仕様書との整合性を確認してください。 