import os
import pickle
import argparse
import boto3
import mlflow
import optuna
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


mlflow.set_tracking_uri(os.getenv("MLFLOW_SITE_URL"))
mlflow.set_experiment("red-wine-quality-hyperopt")
FILENAME = "winequality-red"
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_ENDPOINT = os.getenv("MLFLOW_S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SEED = 0
TARGET = "quality"
FEATURES = ["volatile acidity", "citric acid", "sulphates", "alcohol"]


def read_from_s3(bucket_name, filename: str) -> pd.DataFrame:
    """Read and unpickle dataframe from s3 bucket.
    Keyword Arguments:
        bucket_name: name of the s3 bucket
        filename: name of the file in the bucket

    Returns:
        Dataframe object."""
    s3_resource = boto3.resource("s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=None,
        config=boto3.session.Config(signature_version="s3v4"),
        verify=False
    )
    data = pickle.loads(
        s3_resource.Object(bucket_name=bucket_name, key=filename)\
        .get()["Body"].read()
    )

    return data


def run_optimization(n_trials: int):
    # pylint: disable=redefined-outer-name
    """Run search for n_trials to find
    the best random forest classifier model
    Keyword Arguments:
        n_trials: number of trials to find the best model.

    Returns:
        None"""

    def objective(trial):
        hyperparameter_grid = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 2000, 50),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2"]),
            "max_depth": trial.suggest_int("max_depth", 10, 100, 10),
            "bootstrap": trial.suggest_categorical("bootstrap", [True, False]),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 4, 1),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10, 1),
            "random_state": trial.suggest_int("random_state", SEED, SEED, 1),
            "n_jobs": trial.suggest_int("n_jobs", -1, -1, 1)
        }

        with mlflow.start_run():
            mlflow.set_tag("model", "random_forest_classifier")
            mlflow.log_params(trial.params)
            rfc = Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", RandomForestClassifier(**hyperparameter_grid))
            ])
            rfc.fit(X_train, y_train)
            y_pred = rfc.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            mlflow.log_metric("accuracy", accuracy)

        return accuracy

    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(objective, n_trials=n_trials)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the best parameters for RandomForestClassifier."
    )

    parser.add_argument("n_trials")
    n_trials = int(parser.parse_args().n_trials)

    df = read_from_s3(bucket_name=S3_BUCKET_NAME, filename=FILENAME)
    X_train, X_test, y_train, y_test = \
        train_test_split(df[FEATURES], df[TARGET], random_state=SEED)
    run_optimization(n_trials=n_trials)
