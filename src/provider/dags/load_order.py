from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.kubernetes.secret import Secret
from kubernetes.client import models as k8s

configmaps = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name="postgres-config")),
]

secret_password = Secret(
  deploy_type="env",
  deploy_target="DB_PASSWORD",
  secret="sql-conn"
)

volume = k8s.V1Volume(
  name="order-data-folder",
  persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
    claim_name="order-data-folder"
  )
)

volume_mount = k8s.V1VolumeMount(
  name="order-data-folder",
  mount_path="/app/data/to_ingest"
)

with DAG(
  dag_id='ETL_data_movie',
  tags=['send', 'System Recommandation'],
  # default_args={
  #   'owner': 'airflow',
  #   'start_date': days_ago(0, minute=1),
  #   },
  schedule_interval=None, #'* * * * *',
  # catchup=False
) as dag:
    
    # python_transform = KubernetesPodOperator(
    #     task_id="python_transform",
    #     image="leutergmail/order-python-transform",
    #     cmds=["python3", "main.py"],
    #     on_finish_action="delete_pod",
    #     volumes=[volume],
    #     volume_mounts=[volume_mount]
    # )

    send_to_database = KubernetesPodOperator(
        namespace="airflow",
        task_id="send-to-database",
        image="leutergmail/send-to-database",
        cmds=["python3", "main.py"],
        secrets=[secret_password],
        volumes=[volume],
        volume_mounts=[volume_mount],
        env_from=configmaps
        # on_finish_action="delete_pod",
    )

send_to_database
# python_transform >> python_load