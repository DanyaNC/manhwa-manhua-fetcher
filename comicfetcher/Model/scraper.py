from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from Model.comic import Comic
import shutil
import lxml
import re
import requests
import csv
from collections import deque



# #Test method for first practicing on a local file of the website's downloaded html file
# def open_html():
#     with open("C:/Users/Danya/Desktop/SDE/manhwa-manhua-fetcher/Test_HTML-Website/html_test.html", "r") as f:
#         html_file = BeautifulSoup(f, "lxml")
#     return html_file


    
def open_html(URL):
    html_file = requests.get(URL).text
    return html_file



def process_html(comic : Comic):
    URL = comic.get_url()
    # soup = open_html()
    html_file = open_html(URL)
    
    soup = BeautifulSoup(html_file, "lxml")
    
    latest_chapter = soup.find('li', class_ = 'wp-manga-chapter')


    #Stores 2 strings in a list, which are of the format:
    #Chapter ###, indicating the chapter's number,
    #A line stating how long ago the chapter was uploaded (e.g. 30 mins ago, 2 days ago)
    latest_chapter_info : list = list(latest_chapter.text.strip().replace('\t', '').split('\n'))
    #print(latest_chapter_info)  
    #Extract integers from the chapter number string. Use this to check if it is greater than the
    #previously checked number stored in our data.
    latest_chapter_number = get_chapter_number(latest_chapter_info)
    #print(latest_chapter_number)
    #If the html has a chapter newer than what we have stored as being the last, it is a new chapter
    if(latest_chapter_number > int(comic.get_latest_chapter())):
        #new_chapters contains lists of each chapter's info
        #Chapter #, and Date Posted
        new_chapters = deque()
        #Append our initial gotten info because we know that it is a new chapter
        latest_chapter_url = latest_chapter.a['href']
        # print(f"The latest chapter url is: {latest_chapter_url}")
        latest_chapter_info.append(latest_chapter_url)
        # print(f"The info with url appended: {latest_chapter_info}")
        new_chapters.appendleft(latest_chapter_info)

        #Retrieve our last read/checked chapter for our end boundary of loop
        old_chapter_number = int(comic.get_latest_chapter())
        #We are now checking chapters one by one so using name next instead of last as they are no longer the last
        next_chapter = latest_chapter
        next_chapter_number = latest_chapter_number

        #Iterate through the siblings of the li class tree, aka the chapters,
        #until we are no longer dealing with new chapters. Each chapter's info (Chapter # and date)
        #gets added to the queue as well as it's URL.
        while(next_chapter_number > old_chapter_number+1):
            #Try block because it is possible website messed up an upload,
            #resulting in improper naming, no url associated with a chapter, or other errors.
            try:
                next_chapter = next_chapter.find_next_sibling('li')
                next_chapter_url = next_chapter.a['href']
                next_chapter_info = next_chapter.text.strip().replace('\t', '').split('\n')
                next_chapter_info.append(next_chapter_url)
                next_chapter_number = get_chapter_number(next_chapter_info)
                new_chapters.append(next_chapter_info)
            except:
                print("Error occured while looping through chapters")
                break
        comic.set_latest_chapter(str(latest_chapter_number))
    return new_chapters

    


def get_chapter_number(latest_chapter_info : list):
    return int(re.search(r'\d+', latest_chapter_info[0]).group())

    


def main():
    pass


if __name__ == "__main__":
    main()