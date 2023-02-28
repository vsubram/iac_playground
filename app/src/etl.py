import psycopg2
from psycopg2 import Error
import os
from project_variables import DB_TABLE, DB_VIEW


def create_pg_connection():

    """
    Create a Postgres DB connection capturing details from the env file

    :return: tuple of cursor and connection, which will be used in other functions to execute queries on the Postgres DB 
    """

    # Create connection to postgres
    connection = psycopg2.connect(host=os.environ.get('POSTGRES_HOST'),
                                  port=os.environ.get('POSTGRES_PORT'),
                                  user=os.environ.get('POSTGRES_USER'),
                                  password=os.environ.get('POSTGRES_PASSWORD'),
                                  dbname=os.environ.get('POSTGRES_DB'),
                                  sslmode='allow')
    # Ensure data is added to the database immediately after write commands
    connection.autocommit = True
    cursor = connection.cursor()
    return cursor, connection


def check_table(cursor):

    """
    Check if the table exists.

    :return: Boolean value - TRUE or False for the table that was checked
    """

    cursor.execute(
        "select exists(select * from information_schema.tables where table_name=%s)", (DB_TABLE,))
    table_status = bool(cursor.fetchone()[0])
    return table_status


# def validate_pg_connection(cursor):
#     cursor.execute("SELECT timeofday();", ('Connection to postgres successful!',))
#     print(cursor.fetchone())


def create_table(cursor, table):

    """
    Create a table specified by the user
    :param cursor: Postgres DB cursor
    :param table: Name of the Table to be created
    :return: None
    """

    try:

        print(
            f"Table: {table} does not exist in database: {os.environ.get('POSTGRES_DB')}")
        print(f"Creating table {table} ...")

        create_query: str = """
            CREATE TABLE IF NOT EXISTS jobs (
                job_position_id INT,
                position_title TEXT,
                job_publish_date TIMESTAMP NOT NULL,
                org_name TEXT,
                position_location_display TEXT,
                job_location Text,
                in_multiple_locations BOOLEAN,
                job_url TEXT,
                min_salary_range FLOAT,
                max_salary_range FLOAT,
                record_created_date TIMESTAMP NOT NULL,
                search_parameters TEXT,
                created_by TEXT,
                UNIQUE (job_position_id, search_parameters)
            );
        """

        cursor.execute(create_query)
        print(f"Table creation complete.")

    except Error as e:
        print(e)


def create_view(cursor, view):
    
    """
    Create a view specified by the user
    :param cursor: Postgres DB cursor
    :param view: Name of the view to be created
    :return: None
    """

    try:
        print(
            f"View: {view} does not exist in database: {os.environ.get('POSTGRES_DB')}")
        print(f"Creating view {view} ...")

        create_query: str = """
            -- public.chicago_jobs source

            CREATE OR REPLACE VIEW public.chicago_jobs
            AS select
                jobs.job_publish_date,        
                jobs.position_title,
                jobs.org_name,
                jobs.position_location_display,
                jobs.in_multiple_locations,
                jobs.job_location,
                jobs.job_url,
                jobs.min_salary_range,
                jobs.max_salary_range,
                jobs.search_parameters
            from
                jobs
            where
                jobs.job_publish_date > (
                select
                    date_trunc('month', current_date))
                and
                    (
                        jobs.job_location like '%Chicago%'
                    or jobs.position_location_display like '%Multiple%'::text
                    or jobs.position_location_display = 'Anywhere in the U.S. (remote job)'
                    )
            order by
                jobs.job_publish_date desc
            limit 30;
        """

        cursor.execute(create_query)
        print(f"View creation complete.")

    except Error as e:
        print(e)


def db_populate(rows, table):

    """
    Inspect if table and the view is present in DB. 
    If not create them first, else insert records into the Postgres DB to specified table.
    :param rows: Responses from USA Jobs API for given Keyword, stored as List of tuples
    :param table: Name of the table where the records will be inserted to
    :return: None
    """

    # Create a Connection and Cursor for the records to be inserted to Postgres
    print("Creating the database connection... ")
    cursor, conn = create_pg_connection()

    table_status = check_table(cursor)

    if not table_status:
        create_table(cursor, table)
        create_view(cursor, DB_VIEW)
        insert_records(cursor, rows, table)
    else:
        insert_records(cursor, rows, table)

    cursor.close()
    conn.close()


def insert_records(cursor, rows, table):
    """
    Insert records into the Postgres DB to specified table.
    :param cursor: Postgres DB cursor
    :param rows: Responses from USA Jobs API for given Keyword, stored as List of tuples
    :param table: Name of the table where the records will be inserted to
    :return: None
    """

    before_insert_row_count = get_current_records_connection()

    if table == "jobs":

        try:

            for row in rows:
                insert_query = """INSERT INTO jobs (
                                        job_position_id,
                                        position_title,
                                        job_publish_date,
                                        org_name,
                                        position_location_display,
                                        job_location,
                                        in_multiple_locations,
                                        job_url,
                                        min_salary_range,
                                        max_salary_range,
                                        record_created_date, 
                                        search_parameters, 
                                        created_by
                                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (job_position_id, search_parameters) DO NOTHING"""

                record_to_insert = (row[0], row[1], row[2], row[3], row[4], row[5],
                                    row[6], row[7], row[8], row[9], row[10], row[11], row[12])

                cursor.execute(insert_query, record_to_insert)

        except Error as e:
            print(e)

        after_insert_row_count = get_current_records_connection()

        row_counts = after_insert_row_count - before_insert_row_count

        print(f"Table                   : {table}")
        print(f"Total Records Inserted  : {row_counts}")


def extract_date(date_str) -> str:
    return date_str.split("T")[0]


def get_current_records_connection():

    """
    Get the record counts for the specified table.

    :return: None
    """

    # Create a Connection and Cursor for the records to be inserted to Postgres
    print("Creating the database connection... ")
    cursor, conn = create_pg_connection()

    row_count = 0

    try:
        cursor.execute(f"SELECT COUNT(*) FROM {DB_TABLE}")
        row_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

    except Error as e:
        print(e)

    return row_count


def summarized_city_report():
    """
    Provides the list of rows which will be used in sending out a daily use CSV report
    of the most recent jobs posted in Chicago area
    :return: List[tuple]
    """

    # Create a Connection and Cursor for the records to be inserted to Postgres
    print("Creating the database connection... ")
    cursor, conn = create_pg_connection()

    create_query: str = """
        SELECT 
            position_title,
            job_publish_date,
            org_name,
            position_location_display,
            in_multiple_locations,
            job_url,
            min_salary_range,
            max_salary_range
        FROM chicago_jobs;
    """
    try:
        cursor.execute(create_query)
    except Error as e:
        print(e)
    
    report = cursor.fetchall()

    cursor.close()
    conn.close()

    return report
