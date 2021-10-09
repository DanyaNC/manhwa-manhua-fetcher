from Controller import csv_control
from View import email_formatter

def main(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": ""
    }
    csv_control.main()

    return response


if __name__ == "__main__":
    main("s", "s")
