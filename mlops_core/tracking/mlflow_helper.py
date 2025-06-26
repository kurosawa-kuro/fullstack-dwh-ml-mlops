"""
MLflow integration helper for MLOps projects
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import mlflow
from mlflow.tracking import MlflowClient

from ..config.loader import get_config


class MLflowHelper:
    """MLflow統合ヘルパークラス"""
    
    def __init__(self, experiment_name: Optional[str] = None):
        self.config = get_config()
        self.experiment_name = experiment_name or self.config.mlflow_experiment_name
        self.tracking_uri = self.config.mlflow_tracking_uri
        
        # MLflow設定
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        
        self.client = MlflowClient()
    
    def start_run(self, run_name: Optional[str] = None) -> mlflow.ActiveRun:
        """実験実行を開始"""
        return mlflow.start_run(run_name=run_name)
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """パラメータをログ"""
        mlflow.log_params(params)
    
    def log_metrics(self, metrics: Dict[str, float]) -> None:
        """メトリクスをログ"""
        mlflow.log_metrics(metrics)
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """アーティファクトをログ"""
        mlflow.log_artifact(local_path, artifact_path)
    
    def log_model(self, model, artifact_path: str) -> None:
        """モデルをログ"""
        mlflow.sklearn.log_model(model, artifact_path)
    
    def get_experiment_id(self) -> str:
        """実験IDを取得"""
        experiment = self.client.get_experiment_by_name(self.experiment_name)
        return experiment.experiment_id if experiment else None
    
    def list_runs(self, max_results: int = 100) -> list:
        """実行履歴を取得"""
        experiment_id = self.get_experiment_id()
        if experiment_id:
            return self.client.search_runs(
                experiment_ids=[experiment_id],
                max_results=max_results
            )
        return []
    
    def get_best_run(self, metric: str, ascending: bool = True) -> Optional[mlflow.entities.Run]:
        """最良の実行を取得"""
        runs = self.list_runs()
        if not runs:
            return None
        
        # メトリクスでソート
        sorted_runs = sorted(
            runs,
            key=lambda run: run.data.metrics.get(metric, float('inf') if ascending else float('-inf')),
            reverse=not ascending
        )
        
        return sorted_runs[0] if sorted_runs else None 