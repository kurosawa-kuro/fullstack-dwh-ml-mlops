"""
dbtを使用してrawデータをStaging層に取り込むスクリプト
"""

import subprocess
import sys
import os
from pathlib import Path
from loguru import logger


def run_dbt_ingestion():
    """dbtを使用してrawデータをStaging層に取り込み"""
    
    # dbtプロジェクトディレクトリのパスを取得
    script_dir = Path(__file__).parent
    dbt_project_dir = script_dir.parent / "dbt"
    dbt_project_file = dbt_project_dir / "dbt_project.yml"
    
    if not dbt_project_file.exists():
        logger.error("❌ dbt_project.ymlが見つかりません。dbtプロジェクトディレクトリで実行してください。")
        return False
    
    logger.info(f"dbtプロジェクトディレクトリ: {dbt_project_dir}")
    
    # 仮想環境内のdbtコマンドのパスを取得
    venv_dbt = script_dir.parent.parent / ".venv" / "bin" / "dbt"
    if not venv_dbt.exists():
        logger.error(f"❌ 仮想環境内のdbtコマンドが見つかりません: {venv_dbt}")
        return False
    
    logger.info(f"dbtコマンドパス: {venv_dbt}")
    
    try:
        # dbtプロジェクトディレクトリに移動
        os.chdir(dbt_project_dir)
        
        # dbt depsを実行（依存関係のインストール）
        logger.info("dbt依存関係をインストール中...")
        result = subprocess.run(
            [str(venv_dbt), "deps"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("dbt依存関係インストール完了")
        
        # seedsを実行（CSVファイルの取り込み）
        logger.info("dbt seedsを実行中...")
        result = subprocess.run(
            [str(venv_dbt), "seed"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("dbt seeds実行完了")
        
        # Staging層のモデルを実行
        logger.info("Staging層モデルを実行中...")
        result = subprocess.run(
            [str(venv_dbt), "run", "--select", "staging"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Staging層モデル実行完了")
        
        # テストを実行
        logger.info("dbtテストを実行中...")
        result = subprocess.run(
            [str(venv_dbt), "test", "--select", "staging"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("dbtテスト実行完了")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"dbtコマンド実行エラー: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        return False


if __name__ == "__main__":
    success = run_dbt_ingestion()
    if success:
        logger.info("✅ dbt rawデータ取り込み完了")
    else:
        logger.error("❌ dbt rawデータ取り込み失敗")
        sys.exit(1) 