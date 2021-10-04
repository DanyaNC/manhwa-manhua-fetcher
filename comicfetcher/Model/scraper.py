from genericpath import isfile
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile
from Model.comic import Comic
import shutil
import lxml
import re
import requests
import csv
from collections import deque
import os
from urllib.parse import urlparse


# #Test method for first practicing on a local file of the website's downloaded html file
# def open_html():
#     with open("C:/Users/Danya/Desktop/SDE/manhwa-manhua-fetcher/Test_HTML-Website/html_test.html", "r", encoding='utf8') as f:
#         html_file = BeautifulSoup(f, "lxml")
#     return html_file

ALWAYS_DOWNLOAD_IMG = 0
    
def open_html(URL):
    try:
        html_file = requests.get(URL).text
    except:
        print("Error occured while requesting html from URL in method open_html")
        return
    return html_file



def process_html(comic : Comic):
    URL = comic.get_url()
    # soup = open_html()
    html_file = open_html(URL)
    
    #Possible that we failed to retrieve the htmlfile, in which case, don't
    #attempt the rest of the method
    if(html_file is None):
        return

    domain_name = urlparse(URL).netloc
    chapter_queue = None
    if(domain_name == "reaperscans.com"):
        chapter_queue = process_reaper_scans(html_file, comic)
        return chapter_queue
    elif(domain_name == "asurascans.com" or domain_name == "flamescans.org"):
        chapter_queue = process_asura_flame_scans(html_file, comic)
    else:
        print("Incompatible website provided as URL")
        return chapter_queue
    
    


    
    
def derive_image_path(url : str, comic_name : str):
    file_format = os.path.splitext(url)[1]
    comic_name = comic_name.replace(" ", "")
    local_filename = f"comicfetcher/Model/imgs/{comic_name}{file_format}"
    return local_filename



def process_reaper_scans(html_file : str, comic : Comic) -> deque:
    soup = BeautifulSoup(html_file, "lxml")
    
    latest_chapter = soup.find('li', class_ = 'wp-manga-chapter')

    #Stores 2 strings in a list, which are of the format:
    #Chapter ###, indicating the chapter's number,
    #A line stating how long ago the chapter was uploaded (e.g. 30 mins ago, 2 days ago)
    latest_chapter_info : list = list(latest_chapter.text.strip().replace('\t', '').split('\n'))
 
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
        #try:
        comic_image_url = soup.find('a', id = 'roi')
        path_to_image = retrieve_reaper_image(comic_image_url, comic.get_name(), soup)
        new_chapters.appendleft(path_to_image)
           
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
                #Loop variable changes here, gets decreased as we go down list of chapters
                next_chapter_number = get_chapter_number(next_chapter_info)
                new_chapters.append(next_chapter_info)
            except:
                print("Error occured while looping through chapters")
                break
        comic.set_latest_chapter(str(latest_chapter_number))
        return new_chapters
    else:
        #No new chapter was found, return.
        return

def process_asura_flame_scans(html_file : str, comic : Comic) -> deque:
    soup = BeautifulSoup(html_file, "lxml")
    any_int = re.compile('^[-+]?[0-9]+$')
    latest_chapter = soup.find('li', attrs={"data-num" : any_int})
    
    

def retrieve_reaper_image(comic_image_url : str, comic_name : str, soup) -> str:
    if(comic_image_url is None):
            comic_image_url = soup.find('div', class_='summary_image')       
            comic_image_url = comic_image_url.find('img')['data-srcset'].split(',')[1].strip().split(" ")[0]
            print(comic_image_url)
            #new_chapters.appendleft(download_file(comic_image_url, comic_name.replace(' ', '_')))
    else:
        comic_image_url = comic_image_url.find('img')['data-srcset'].split(',')[1].strip().split(" ")[0]
        print(comic_image_url)
        #new_chapters.appendleft(download_file(comic_image_url, comic_name.replace(' ', '_')))
    if(comic_image_url is None):
        print("Unable to get the URL for the cover image, perhaps the site's HTML changed?")
        return None
    else:
        image_file_path = derive_image_path(comic_image_url, comic_name)
        if(os.path.isfile(image_file_path) and ALWAYS_DOWNLOAD_IMG == 0):
            #Image already exists, no need to download it for this comic.
            print(f"Image for {comic_name} is already downloaded.")
            pass
        else:
            download_file(comic_image_url, image_file_path)
        return image_file_path


#Referenced from https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_file(url : str, local_filename : str):
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    if(r.status_code == 200):
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    else:
        print("Failed to download image")
        local_filename = None
    return local_filename

def get_chapter_number(latest_chapter_info : list):
    return int(re.search(r'\d+', latest_chapter_info[0]).group())

    


def main():
    pass


if __name__ == "__main__":
    main()