### Wine Quality Prediction

The [dataset](https://archive.ics.uci.edu/dataset/186/wine+quality) used in the project is red wine quality scores of the Portuguese 'Vinho Verde' and their corresponding physicochemical tests.

#### How to run all this stuff
- run docker-compose build in the root folder;
- run docker-compose up -d in the root folder;
- open http://localhost:9001 in your browser;
- login to the minio portal and create a new bucket via Buckets -> Create Bucket button with name "mlflow-artifacts";
- create access keys via Access Keys -> Create access key button;
- copy Access Key (MINIO_ACCESS_KEY) and Secret Key (MINIO_SECRET_KEY) to the existing .env file;
- run docker-compose down and docker-compose up -d to re-initialize new minio API keys;

#### Jupyter
- to open jupyter you need to reach http://localhost:8888/lab in your browser.
- open ./jupyter/main.ipynb and run the download_data.py cell. It will pull the zip file with data and save it to the "mlflow_artifacts" bucket;
- optional step: run explore_features.ipynb if you want to understand the idea behind chosen features;
- optional step: run initial_models.ipynb to see the performance of the 4 main classification models with default parameters;
- in ./jupyter/main.ipynb run hpo.py for hyperparameter optimization.

#### Prefect
The model could be promoted to the model registry in two ways:
- run register_best_model.py for manual prefect flow registration OR
- run register_minio_block.py & !prefect deployment build cells for scheduled prefect flow deployment.
Either way you'll end up with the following prefect flow:
![Prefect Flow](./resources/prefect_flow_deployment.png "Prefect flow")

<center>Figure 1. Prefect flow</center>

This flow consists of three steps:
- "Prepare Data" downloads file from s3 bucket and splits dataset into training and validation parts;
- "Get Parameters" pulls the parameters of the best model from hyperparameter optimization experiment;
- "Register Best Model" trains the model, logs its artifacts and promotes it to the model registry.

#### Known issues
On linux machines ds-notebook container might not start because of privileges issue. If you encounter this problem you need to change ownership of the jupyter folder to the docker user with the command "sudo chown -R 100999:100099 ./jupyter".

#### TODO
- add minio bucket creation container;
- rewrite minio section;
- add architecture schema.