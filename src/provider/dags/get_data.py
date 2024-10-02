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
  name="data-folder",
  persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(
    claim_name="data-folder"
  )
)

volume_mount = k8s.V1VolumeMount(
  name="data-folder",
  mount_path="/app/data/to_ingest"
)

env_dict = {"DATE_FOLDER": "{{ logical_date | ds }}"}


with DAG(
  dag_id='injest-data',
  tags=['ETL', 'System Recommandation'],
  # default_args={
  #   'owner': 'airflow',
  #   'start_date': days_ago(0, minute=1),
  #   },
  schedule_interval=None, #'* * * * *',
  # catchup=False
) as dag:
    
  scraping_data = KubernetesPodOperator(
      namespace="airflow",
      task_id="scraping-data",
      image="leutergmail/scraping-data",
      cmds=["python3", "main.py"],
      volumes=[volume],
      volume_mounts=[volume_mount],
      on_finish_action="delete_pod",
      env_vars=env_dict
  )

  extract_features = KubernetesPodOperator(
      namespace="airflow",
      task_id="extract-feature",
      image="leutergmail/extract-feature",
      cmds=["python3", "main.py"],
      on_finish_action="delete_pod",
      volumes=[volume],
      volume_mounts=[volume_mount], 
      env_vars=env_dict
  )

  send_to_database = KubernetesPodOperator(
      namespace="airflow",
      task_id="send-to-database",
      image="leutergmail/send-to-database",
      cmds=["python3", "main.py"],
      secrets=[secret_password],
      volumes=[volume],
      volume_mounts=[volume_mount],
      env_from=configmaps,
      on_finish_action="delete_pod",
      env_vars=env_dict
  )
scraping_data >> extract_features
extract_features >> send_to_database 