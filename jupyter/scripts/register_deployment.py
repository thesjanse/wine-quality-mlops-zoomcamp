from register_best_model import main_flow
from prefect.deployments import Deployment
from prefect.filesystems import RemoteFileSystem


if __name__ == "__main__":
    storage = RemoteFileSystem.load("minio")
    deployment = Deployment.build_from_flow(
        flow=main_flow,
        name="rfc-red-wine",
        version=1,
        work_queue_name="red-wine",
        work_pool_name="default-agent-pool",
        schedule="* * 0 0 0",
        storage=storage
    )

    deployment.apply()
