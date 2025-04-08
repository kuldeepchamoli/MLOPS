from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago

# ---------------- DAG Definition ---------------- #
with DAG(
    dag_id='nasa_apod_postgres',  # DAG name
    start_date=days_ago(1),       # Start 1 day ago from today
    schedule_interval='@daily',   # Run daily
    catchup=False                 # Don't run for missed past intervals
) as dag:

    # ---------------- 1. Create table if not exists ---------------- #
    @task
    def create_table():
        # Connect to Postgres using connection ID set in Airflow UI
        postgres_hook = PostgresHook(postgres_conn_id="my_postgres_connection")

        # SQL to create table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS apod_data(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            explanation TEXT,
            url TEXT,
            date DATE,
            media_type VARCHAR(50)
        );
        """

        # Execute the SQL
        postgres_hook.run(create_table_query)

    # ---------------- 2. Extract NASA API ---------------- #
    extract_apod = SimpleHttpOperator(
        task_id='extract_apod',
        http_conn_id='nasa_api',  # This connection should be configured in Airflow
        endpoint='planetary/apod',
        method='GET',
        data={"api_key": "{{ conn.nasa_api.extra_dejson.api_key }}"},  # Use API key from Airflow connection
        response_filter=lambda response: response.json(),  # Convert response to JSON
        log_response=True
    )

    # ---------------- 3. Transform response ---------------- #
    @task
    def transform_apod_data(response):
        # Pick the necessary fields from the API response
        apod_data = {
            'title': response.get('title', ''),
            'explanation': response.get('explanation', ''),
            'url': response.get('url', ''),
            'date': response.get('date', ''),
            'media_type': response.get('media_type', '')
        }
        return apod_data

    # ---------------- 4. Load data into Postgres ---------------- #
    @task
    def load_data_to_postgres(apod_data):
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection')

        insert_query = """
        INSERT INTO apod_data (title, explanation, url, date, media_type)
        VALUES (%s, %s, %s, %s, %s)
        """

        # Insert the data into the database
        postgres_hook.run(insert_query, parameters=(
            apod_data['title'],
            apod_data['explanation'],
            apod_data['url'],
            apod_data['date'],
            apod_data['media_type']
        ))

    # ---------------- 5. Task Dependencies ---------------- #
    # Run tasks in sequence: create table -> extract -> transform -> load
    # create = create_table()
    # transform = transform_apod_data(extract_apod.output)
    # create >> extract_apod >> transform >> load_data_to_postgres(transform)
    ##Extract
    create_table() >> extract_apod ## ensure table created b4 extraction
    api_response=extract_apod.output
    ##transform
    transformed_data=transform_apod_data(api_response)
    ##Load
    load_data_to_postgres(transformed_data)