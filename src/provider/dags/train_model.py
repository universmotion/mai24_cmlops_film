from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.kubernetes.secret import Secret
from kubernetes.client import models as k8s

configmaps = [
    k8s.V1EnvFromSource(
        config_map_ref=k8s.V1ConfigMapEnvSource(name="postgres-config")),
]

secret_password = Secret(
    deploy_type="env",
    deploy_target="DB_PASSWORD",
    secret="sql-conn"
)

volume = k8s.V1Volume(
    name="model-folder",
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
        claim_name="model-folder"
    )
)

volume_mount = k8s.V1VolumeMount(
    name="model-folder",
    mount_path="/app/data/models"
)

with DAG(
    dag_id='train-model',
    tags=['training-model', 'System Recommandation'],
    default_args={
        'owner': 'romain',
        'start_date': days_ago(0, minute=1),
    },
    schedule_interval='00 8 * * *',
    catchup=False
) as dag:

    train_model = KubernetesPodOperator(
        namespace="airflow",
        task_id="train-model",
        image="leutergmail/train-model",
        cmds=["python3", "main.py"],
        secrets=[secret_password],
        volumes=[volume],
        volume_mounts=[volume_mount],
        env_from=configmaps,
        on_finish_action="delete_pod"
    )

train_model
