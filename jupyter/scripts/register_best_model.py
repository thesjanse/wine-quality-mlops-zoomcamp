import os

import mlflow
import pandas as pd
import prefect

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from hpo import read_from_s3


mlflow.set_tracking_uri(os.getenv("MLFLOW_SITE_URL"))
mlflow.set_experiment("red-wine-quality-production")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_ENDPOINT = os.getenv("MLFLOW_S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
FILENAME = "winequality-red"
EXPERIMENT_NAME = "red-wine-quality-hyperopt"
SEED = 0
TARGET = "quality"
MODEL_FEATURES = ["volatile acidity", "citric acid", "sulphates", "alcohol"]


@prefect.task(name="Prepare Data", retries=3)
def prepare_data(
    bucket_name: str,
    filename: str,
    target: str,
    features: list
    ) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """Read data from s3 bucket and split dataset into training and test.
    Keyword Arguments:
        bucket_name: name of the s3 bucket.
        filename: name of the source file.
        target: name of the target column.
        features: list of str with feature column names.

    Returns:
        A tuple with (x_train, x_test, y_train, y_test) dataframes."""
    data = read_from_s3(bucket_name=bucket_name, filename=filename)
    x_train, x_test, y_train, y_test = \
        train_test_split(data[features], data[target], random_state=SEED)
    return x_train, x_test, y_train, y_test

@prefect.task(name="Get Parameters")
def get_best_params(experiment_name: str) -> dict:
    """Get parameters for the best performing model
    from the mlflow experiment.
    Keyword Arguments:
        experiment_name: name of the mlflow experiment.

    Returns:
        A parameters dictionary."""
    experiment_id = dict(mlflow.get_experiment_by_name(
        experiment_name))["experiment_id"]

    run = mlflow.MlflowClient().search_runs(
        experiment_ids=experiment_id,
        filter_string="",
        max_results=1,
        order_by=["metrics.accuracy DESC", "params.n_estimators ASC"],
    )[0]
    params = run.to_dictionary()["data"]["params"]
    numeric_params = [
        "n_estimators", "max_depth", "min_samples_leaf",
        "min_samples_split", "random_state", "n_jobs"
    ]
    for k in params:
        if k in numeric_params:
            params[k] = int(params[k])
        if params[k] == 'True':
            params[k] = True
        elif params[k] == 'False':
            params[k] = False
    return params


@prefect.task(name="Register Best Model", log_prints=True)
def register_best_model(
    params: dict, x_train, x_test, y_train, y_test: pd.DataFrame):
    """Train and register the random forest classifier model.
    Keyword Arguments:
        params: dict of best parameters for random forest classifier.
        x_train: features train dataframe.
        x_test: features validation dataframe.
        y_train: target train dataframe.
        y_test: target validation dataframe.

    Returns:
        None"""
    with mlflow.start_run():
        mlflow.set_tag("model", "random_forest_classifier")
        rfc = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(**params))
        ])
        rfc.fit(x_train, y_train)
        y_pred = rfc.predict(x_test)
        signature = mlflow.models.infer_signature(x_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", accuracy)

        mlflow.sklearn.log_model(
            sk_model=rfc,
            artifact_path="red-wine-model",
            signature=signature,
            registered_model_name="sk-rfc-model",
        )
    return None


@prefect.flow(name="Main Registration Flow")
def main_flow(
    bucket_name: str = S3_BUCKET_NAME,
    filename: str = FILENAME,
    target: str = TARGET,
    features: list = MODEL_FEATURES,
    experiment_name: str = EXPERIMENT_NAME) -> None:
    # pylint: disable=missing-function-docstring,
    # pylint: disable=dangerous-default-value
    x_train, x_test, y_train, y_test = \
        prepare_data(
            bucket_name=bucket_name,
            filename=filename,
            target=target,
            features=features
        )
    params = get_best_params(experiment_name=experiment_name)
    register_best_model(params, x_train, x_test, y_train, y_test)


if __name__ == "__main__":
    main_flow(
        bucket_name=S3_BUCKET_NAME,
        filename=FILENAME,
        target=TARGET,
        features=MODEL_FEATURES,
        experiment_name=EXPERIMENT_NAME
    )
