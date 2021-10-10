import csv
import time
import shutil
from tempfile import NamedTemporaryFile
from Model import scraper
from Model.comic import Comic
from View import email_formatter
from Model import aws

def parse_csv():
    """
    Open and read a csv file that contains the list of comics,
    which should contain these 3 values separated by a delimiter
    for each comic, Name, Latest_Chapter, URL
    Each line should represent 1 comic.
    Parse the data line by line (comic by comic)
    and create a new Comic object for each line.
    Then feed Comic to scraper to check for new chapters.
    """
    fields = ['Names', 'Last_Chapter', 'URL']
    new_chapter_flag = False
    if not aws.is_uploaded_s3("comics_list.csv"):
        if not aws.upload_to_s3("Model/comics_list.csv"):
            return
    aws.download_csv()
    output_csv = open('/tmp/comics_list.csv', 'w', newline='')
    with open('/tmp/old_comics_list.csv', 'r') as comics_list, output_csv:
        csv_reader = csv.DictReader(comics_list)
        writer = csv.DictWriter(output_csv, fields, delimiter=',')
        writer.writeheader()
        for line in csv_reader:
            info_list = list(dict.values(line))
            comic = Comic(info_list)
            new_chapter_info_queue = scraper.process_html(comic)
            # If an error occured during the processing of the html, or
            # there was no new chapters, we should have a NONE for our queue.
            if(new_chapter_info_queue is None):
                print(f"No queue was made for comic: {comic.get_name()}")
                writer.writerow(line)
            else:
                new_chapter_flag = True
                email_formatter.format_chapter(new_chapter_info_queue, comic.get_name())
                writer.writerow(comic.get_csv_dict())
            time.sleep(12)
    if new_chapter_flag:
        email_formatter.attach_closer()
        aws.upload_to_s3('/tmp/comics_list.csv')
        output_csv.close()
    else:
        print("No new chapters were found. Email not sent")


def main():
    parse_csv()
