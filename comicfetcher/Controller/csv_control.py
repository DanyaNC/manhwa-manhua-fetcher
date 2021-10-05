import csv
from Model import scraper
from Model.comic import Comic
import time


def parse_csv():
    """
    Open and read a csv file that contains the list of comics,
    which should contain these 3 values separated by a delimiter
    for each comic, Name, Latest_Chapter, URL
    Each line should contain 1 comic, 3 values.
    Parse the data line by line (comic by comic)
    and create a new Comic object for each line.
    """
    with open('comicfetcher/Model/comics_list.csv', 'r') as comics_list:
        csv_reader = csv.DictReader(comics_list)
        for line in csv_reader:
            info_list = list(dict.values(line))
            comic = Comic(info_list)
            new_comic_queue = scraper.process_html(comic)
            # If an error occured during the processing of the html, or
            # there was no new chapters, we should have a NONE for our queue.
            if(new_comic_queue is None):
                print(f"No queue was made for comic: {comic.get_name}")
            else:
                print(new_comic_queue)
            time.sleep(5)


def main():
    parse_csv()
