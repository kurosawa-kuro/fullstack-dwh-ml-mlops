"""
RawデータをDuckDBにインポートするスクリプト
Bronze層としてrawデータをそのまま保存
"""

import duckdb
import pandas as pd
from pathlib import Path
from loguru import logger


def create_bronze_table():
    """Bronze層のテーブルを作成し、rawデータをインポート"""
    
    # パス設定
    data_dir = Path("data")
    raw_file = data_dir / "raw" / "house_data.csv"
    db_file = data_dir / "interim" / "house_price_dwh.duckdb"
    
    # ディレクトリ作成
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Rawデータファイル: {raw_file}")
    logger.info(f"DuckDBファイル: {db_file}")
    
    try:
        # DuckDB接続
        con = duckdb.connect(str(db_file))
        logger.info("DuckDB接続成功")
        
        # CSVファイル読み込み
        df_raw = pd.read_csv(raw_file)
        logger.info(f"CSV読み込み完了: {len(df_raw)}行")
        
        # Bronze層テーブル作成
        con.execute("CREATE OR REPLACE TABLE bronze_raw AS SELECT * FROM df_raw")
        logger.info("Bronze層テーブル作成完了")
        
        # テーブル情報確認
        result = con.execute("SELECT COUNT(*) as row_count FROM bronze_raw").fetchone()
        logger.info(f"Bronze層テーブル行数: {result[0]}")
        
        # スキーマ確認
        schema = con.execute("DESCRIBE bronze_raw").fetchall()
        logger.info("Bronze層テーブルスキーマ:")
        for col in schema:
            logger.info(f"  {col[0]}: {col[1]}")
        
        con.close()
        logger.info("DuckDB接続終了")
        
        return True
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        return False


if __name__ == "__main__":
    success = create_bronze_table()
    if success:
        logger.info("✅ Rawデータインポート完了")
    else:
        logger.error("❌ Rawデータインポート失敗") 