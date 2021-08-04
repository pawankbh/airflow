from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

from datetime import datetime, timedelta


# default arguments for each task
default_args = {
    'owner': 'pawan',
    'depends_on_past': False,
    'start_date': datetime(2021, 7, 4),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


dag = DAG('test_s3_download',
          default_args=default_args,
          schedule_interval=None)  # "schedule_interval=None" means this dag will only be run by external commands

TEST_BUCKET = 's3-bucket-to-watch-mlops'
S3_CONN_ID='aws_s3'



# simple download task
def download_file(bucket, key, destination):
    import boto3
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(bucket, key)


# simple upload task
def upload_file(source, bucket, key):
    import boto3
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).upload_file(source, key)


download_from_s3 = PythonOperator(
    task_id='download_from_s3',
    python_callable=download_file,
    op_kwargs={'bucket': TEST_BUCKET, 'key': S3_CONN_ID},
    dag=dag)


sleep_task = BashOperator(
    task_id='sleep_for_1',
    bash_command='sleep 1',
    dag=dag)


upload_to_s3 = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_file,
    op_kwargs={'bucket': TEST_BUCKET, 'key': S3_CONN_ID},
    dag=dag)


download_from_s3.set_downstream(sleep_task)
sleep_task.set_downstream(upload_to_s3)
