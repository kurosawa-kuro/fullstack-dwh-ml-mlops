#!/usr/bin/env python3
"""
dbtパイプライン実行スクリプト
仕様書に基づくSilver LayerとGold Layerの実行
"""

import subprocess
import sys
from pathlib import Path


def run_dbt_command(command, cwd=None):
    """dbtコマンドを実行"""
    if cwd is None:
        cwd = Path(__file__).parent
    
    print(f"実行中: {command}")
    print(f"作業ディレクトリ: {cwd}")
    
    try:
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ 成功")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ エラー")
        print(f"エラーコード: {e.returncode}")
        if e.stdout:
            print("標準出力:")
            print(e.stdout)
        if e.stderr:
            print("エラー出力:")
            print(e.stderr)
        return False


def main():
    """メイン実行関数"""
    print("🏗️ dbtパイプライン実行開始")
    print("=" * 50)
    
    # 1. dbt依存関係のインストール
    print("\n📦 dbt依存関係のインストール")
    if not run_dbt_command("dbt deps"):
        sys.exit(1)
    
    # 2. モデルの実行（Silver Layer）
    print("\n🥈 Silver Layer実行")
    if not run_dbt_command("dbt run --select silver"):
        sys.exit(1)
    
    # 3. テストの実行（Silver Layer）
    print("\n🧪 Silver Layerテスト")
    if not run_dbt_command("dbt test --select silver"):
        sys.exit(1)
    
    # 4. モデルの実行（Gold Layer）
    print("\n🥇 Gold Layer実行")
    if not run_dbt_command("dbt run --select gold"):
        sys.exit(1)
    
    # 5. テストの実行（Gold Layer）
    print("\n🧪 Gold Layerテスト")
    if not run_dbt_command("dbt test --select gold"):
        sys.exit(1)
    
    # 6. ドキュメント生成
    print("\n📚 ドキュメント生成")
    if not run_dbt_command("dbt docs generate"):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ dbtパイプライン実行完了")
    print("\n📊 生成されたアーティファクト:")
    print("- Silver Layer: silver_house_data")
    print("- Gold Layer: ft_house_ml")
    print("- 前処理アーティファクト: target/preprocessing_artifacts/")
    print("- ドキュメント: target/index.html")


if __name__ == "__main__":
    main() 