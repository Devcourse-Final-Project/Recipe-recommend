from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago


dag = DAG(
    dag_id="web_s3_to_redshift_bulk_update",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
)

# 테이블 삭제
drop_table = PostgresOperator(
    task_id="drop_table",
    postgres_conn_id="redshift_dev_db",  # The connection id in Airflow Connections.
    sql="DROP TABLE IF EXISTS raw_data.web_recipe;",
    dag=dag,
)

# 테이블 생성
create_table = PostgresOperator(
    task_id="create_table",
    postgres_conn_id="redshift_dev_db",  # The connection id in Airflow Connections.
    sql="""
        CREATE TABLE raw_data.web_recipe (
            web_id INT,
            food_name VARCHAR(MAX),
            food_img VARCHAR(255),
            views INT,
            serving VARCHAR(255),
            timer VARCHAR(255),
            difficulty VARCHAR(255),
            ingredient VARCHAR(MAX),
            created_date VARCHAR(255),
            recipe_link VARCHAR(255),
            reviews INT,
            comments INT,
            ingredient_name1 VARCHAR(255),
            ingredient_name2 VARCHAR(255),
            ingredient_name3 VARCHAR(255),
            ingredient_name4 VARCHAR(255),
            ingredient_name5 VARCHAR(255),
            ingredient_name6 VARCHAR(255),
            ingredient_name7 VARCHAR(255),
            ingredient_name8 VARCHAR(255),
            ingredient_name9 VARCHAR(255),
            ingredient_name10 VARCHAR(255),
            ingredient_unit1 VARCHAR(255),
            ingredient_unit2 VARCHAR(255),
            ingredient_unit3 VARCHAR(255),
            ingredient_unit4 VARCHAR(255),
            ingredient_unit5 VARCHAR(255),
            ingredient_unit6 VARCHAR(255),
            ingredient_unit7 VARCHAR(255),
            ingredient_unit8 VARCHAR(255),
            ingredient_unit9 VARCHAR(255),
            ingredient_unit10 VARCHAR(255)
        );
        """,
    dag=dag,
)

bulk_update = S3ToRedshiftOperator(
    task_id="s3_to_redshift",
    schema="raw_data",  # Your RedShift Schema here.
    table="web_recipe",  # Your RedShift Table here.
    s3_bucket="de-2-3-airflow",
    s3_key="test/recipe/merge_recipe/web_merge_data_23-09-02_16:31:39.csv",
    copy_options=["csv", "MAXERROR 1", "IGNOREHEADER 1"],
    aws_conn_id="aws_conn_id",
    redshift_conn_id="redshift_dev_db",  # The connection id in Airflow Connections.
    dag=dag,
)

# Task dependency 설정
drop_table >> create_table >> bulk_update
