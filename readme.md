### Wine Quality Prediction

The dataset[https://archive.ics.uci.edu/dataset/186/wine+quality] used in the project is red wine quality scores of the Portuguese 'Vinho Verde' and their corresponding physicochemical tests.

#### How to run all this stuff
- run docker-compose build in the root folder;
- run docker-compose up -d in the root folder;
- open http://localhost:9001 in your browser;
- login to the minio portal and create a new bucket via Buckets -> Create Bucket button with name "mlflow-artifacts";
- create access keys via Access Keys -> Create access key button;
- copy Access Key (MINIO_ACCESS_KEY) and Secret Key (MINIO_SECRET_KEY) to the existing .env file;
- run docker-compose down and docker-compose up -d to re-initialize new minio API keys;

- open ./jupyter/main.ipynb and run the download_data.py cell. It will pull the zip file with data and save it to the "mlflow_artifacts" bucket;
- optional step: run explore_features.ipynb if you want to understand the idea behind chosen features;
- optional step: run initial_models.ipynb to see the performance of the 4 main classification models with default parameters;
- open ./jupyter/main.ipynb and run hpo.py for hyperparameter optimization.

#### Known issues
On linux machines ds-notebook container might not start because of privileges issue. If you encounter this problem you need to change ownership of the jupyter folder to the docker user with the command "sudo chown -R 100999:100099 ./jupyter".