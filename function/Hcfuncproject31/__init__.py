## This folder will contains the Azure function code.

## Note:

##- Before deploying, be sure to update your requirements.txt file by running `pip freeze > requirements.txt`
##- Known issue, the python package `psycopg2` does not work directly in Azure; install `psycopg2-binary` instead to use the `psycopg2` library in Azure

##The skelton of the `__init__.py` file will consist of the following logic:
import logging
import azure.functions as func
import psycopg2
import os
import settings
import json
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database hc
    connection = psycopg2.connect("dbname ={0} user={1} password={2} host={3}".format(settings.POSTGRES_DB,settings.POSTGRES_USER,settings.POSTGRES_PW,settings.POSTGRES_URL))
    cursor = connection.cursor()
    try:
        # TODO: Get notification message and subject from database using the notification_id
        query = cursor.execute("SELECT message, subject FROM notification WHERE id = {};".format(notification_id))

        # TODO: Get attendees email and name   
        cursor.execute("SELECT first_name, last_name, email FROM attendee;")
        # TODO: Loop through each attendee and send an email with a personalized subject
        count = 0
        for attendee in cursor.fetchall():
            count += 1
            first_name = attendee[0]
            last_name = attendee[1]
            email = attendee[2]        
            from_email = "hoang.scv@gmail.com"

            Mail('{}, {}, {}'.format({from_email}, {email}, {query}))
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        status = "Notified {} attendees".format(count)
        date = datetime.utcnow()
        cursor.execute("UPDATE notification SET status = '{}', completed_date = '{}' WHERE id = {};".format(status, date, notification_id))        
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        cursor.close()
        connection.close()
