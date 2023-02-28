from api_helper import api_results
from project_variables import DB_TABLE, OUTPUT_PATH, SENDER_EMAIL
from etl import db_populate, summarized_city_report
from send_email import write_to_csv, send_report


if __name__ == "__main__":
    
    # Extract records to be inserted from USA Jobs API
    print("Preparing records to be inserted from Jobs API... ")
    rows = api_results()

    # Create a Connection and Cursor for the records to be inserted to Postgres
    print("Inserting new records to the table... ")
    db_populate(rows=rows, table=DB_TABLE)

    # 5. Extract averages, write to csv and email it
    print("Preparing the report... ")
    report = summarized_city_report()
    write_to_csv(report, OUTPUT_PATH)
    send_report(OUTPUT_PATH, SENDER_EMAIL)

    print("Report sent. ")

    print("Exiting program.")

    
