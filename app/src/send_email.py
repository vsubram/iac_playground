import os
import csv
from datetime import date
from typing import List

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def write_to_csv(report: List[tuple], CSV_PATH: str):
    """
    Writes the provided list of tuples to a OUTPUT_PATH csv file.

    :param report List[tuple]: Report obtained from extract_averages()
    :param CSV_PATH str: Output path for the csv file
    :return: None
    """

    c = csv.writer(open(CSV_PATH, "w"))

    column_names = [
        "position_title",
        "job_publish_date",
        "org_name",
        "position_location_display",
        "in_multiple_locations",
        "job_url",
        "min_salary_range",
        "max_salary_range"
    ]

    c.writerow(column_names)
    c.writerows(report)


def send_report(CSV_PATH, RECIPIENT_EMAIL):
    """
    Sends the CSV_PATH.csv file to the recipient email.

    :param CSV_PATH str: Path of the output csv file
    :param RECIPIENT_EMAIL str:
    """

    msg = MIMEMultipart()

    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = "USA Jobs - Monthly top 30 Jobs related to Data Engineering in Chicago Area"

    body = '''
        In the attachment you can find the daily .csv file containing list of Data Engineering related jobs in Chicago.
        The list will be updated if there any new jobs for the month, displaying most recently posted job.
    '''
    msg.attach(MIMEText(body, "plain"))

    filename = f"{date.today()} - Data jobs report.csv"
    attachment = open(CSV_PATH, "rb")
    p = MIMEBase("application", "octet-stream")
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "attachment; filename= %s" % filename)

    msg.attach(p)

    # If sender is using Gmail, make sure to enable less secure apps in Account Settings
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASS"))
    text = msg.as_string()
    s.sendmail(os.getenv("SENDER_EMAIL"), RECIPIENT_EMAIL, text)
    s.quit()