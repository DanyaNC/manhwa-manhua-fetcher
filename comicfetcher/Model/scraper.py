from bs4 import BeautifulSoup
from bs4.element import Tag
from Model.comic import Comic
from Model import aws
import lxml
import re
import requests
from collections import deque
import os
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError


# Test method for first practicing on a local file
# of the website's downloaded html file
# def open_html():
#     with open("Test_HTML-Website/heavenly_martial_god.html", "r", encoding='utf8') as f:
#         html_file = f.read()
#     return html_file
# TODO: Always delete IMG constant
ALWAYS_DOWNLOAD_IMG = 0
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
s3 = boto3.client('s3')

def open_html(URL):
    try:
        html_file = requests.get(URL, headers=HEADERS).text
    except Exception:
        print("Error occured requesting html from URL in method open_html")
        return
    return html_file


def process_html(comic: Comic):
    URL = comic.get_url()
    # soup = open_html()
    html_file = open_html(URL)
    # Possible that we failed to retrieve the htmlfile, in which case, don't
    # attempt the rest of the method
    if(html_file is None):
        return
    domain_name = urlparse(URL).netloc
    chapter_queue = None
    if(domain_name == "reaperscans.com"):
        chapter_queue = process_reaper_scans(html_file, comic, "reaperscans")
        return chapter_queue
    elif(domain_name == "www.asurascans.com" or domain_name == "flamescans.org"):
        chapter_queue = process_asura_flame_scans(html_file, comic, "asuraflame")
        return chapter_queue
    else:
        print("Incompatible website provided as URL")
        return chapter_queue


def derive_local_image_path(url: str, comic_name: str):
    file_format = get_file_format(url)
    comic_name_no_spaces = remove_spaces(comic_name)
    local_filename = f"/tmp/{comic_name_no_spaces}{file_format}"
    return local_filename


def get_file_format(url: str) -> str:
    image_file_format = os.path.splitext(url)[1]
    return image_file_format

def remove_spaces(comic_name: str) -> str:
    return comic_name.replace(" ", "")


def process_reaper_scans(html_file: str, comic: Comic, domain_name: str) -> deque:
    soup = BeautifulSoup(html_file, 'lxml')

    latest_chapter = soup.find('li', class_='wp-manga-chapter')

    # Stores 2 strings in a list, which are of the format:
    # Chapter ###, indicating the chapter's number, and
    # a line stating how long ago the chapter was uploaded
    # (e.g. 30 mins ago, 2 days ago)
    latest_chapter_info: list = get_chapter_info(latest_chapter)

    # Extract integers from the chapter number string.
    # Use this to check if it is greater than the
    # previously checked number stored in our data.
    latest_chapter_number = get_chapter_number(latest_chapter_info)

    # If the html has a chapter newer than what we have stored
    # as being the last, it is a new chapter
    old_chapter_number = int(comic.get_latest_chapter())
    if(latest_chapter_number > old_chapter_number+1):
        new_chapters = get_all_new_chapters(latest_chapter, latest_chapter_info,
                                            domain_name, latest_chapter_number, comic, soup)
        return new_chapters
    else:
        # No new chapters were found, return.
        return None


def process_asura_flame_scans(html_file: Tag, comic: Comic, domain_name: str) -> deque:
    soup = BeautifulSoup(html_file, "lxml")
    any_int = re.compile('^[-+]?[0-9]+$')
    latest_chapter_html = soup.find('li', attrs={'data-num': any_int})
    # Stores 2 strings in a list, which are of the format:
    # Chapter ###, indicating the chapter's number,
    # A line stating how long ago the chapter was uploaded
    # (e.g. 30 mins ago, 2 days ago)
    latest_chapter_info = get_chapter_info(latest_chapter_html)

    latest_chapter_number = get_chapter_number(latest_chapter_info)
    old_chapter_number = int(comic.get_latest_chapter())
    if(latest_chapter_number > old_chapter_number+1):
        new_chapters = get_all_new_chapters(latest_chapter_html, latest_chapter_info,
                                            domain_name, latest_chapter_number, comic, soup)
        return new_chapters
    else:
        # No new chapters were found
        return None


def get_comic_image(comic_name: str, soup, domain_name: str) -> str:
    if(domain_name == "reaperscans"):
        image_url = parse_reaper_image_url(soup)
    elif(domain_name == "asuraflame"):
        image_url = parse_asuraorflame_image_url(soup)
    if(image_url is not None):
        local_image_file_path = derive_local_image_path(image_url, comic_name)
        if(aws.is_uploaded_s3(local_image_file_path)):
            print(f"Image for {comic_name} is already present in s3 bucket.")
            return aws.get_s3_url(local_image_file_path)
        else:
            if(download_file(image_url, local_image_file_path)):
                if(aws.upload_to_s3(local_image_file_path)):
                    print(f"Uploaded {comic_name} image to s3")
                    return aws.get_s3_url(local_image_file_path)
    return None


def parse_reaper_image_url(soup) -> str:
    # Find location of the img URL in the HTML
    comic_image_url = soup.find('a', id='roi')
    if(comic_image_url is None):
        # Not an animated img page, need different approach
        comic_image_url = soup.find('div', class_='summary_image')
        # Extract the URL
        comic_image_url = comic_image_url.find('img')['data-srcset'].split(',')[1].strip().split(" ")[0]
    else:
        # Extract the URL
        comic_image_url = comic_image_url.find('img')['data-srcset'].split(',')[1].strip().split(" ")[0]
    if(comic_image_url is None):
        print("Unable to get the URL for the cover image, perhaps the site's HTML changed?")
        return None
    return comic_image_url


def parse_asuraorflame_image_url(soup) -> str:
    comic_image_url = soup.find('div', class_='thumb').find('img')['src']
    if(comic_image_url is None):
        print("Unable to get image URL for asura/flame, perhaps the site's HTML changed?")
    return comic_image_url


# Referenced from https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_file(url: str, local_filename: str) -> bool:
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    print(os.getcwd())
    if(r.status_code == 200):
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    else:
        print("Failed to download image")
        return False
    return True


def get_all_new_chapters(latest_chapter: Tag, latest_chapter_info: list,
                         domain_name: str, latest_chapter_number: int, comic: Comic, soup: BeautifulSoup) -> deque:
    # new_chapters contains lists of each chapter's info
    # Chapter #, and Date Posted
    # As well as a file path to the comic's cover image at the front of the queue.
    new_chapters = deque()
    # Append our initial gotten info because we know that it is a new chapter
    latest_chapter_url = latest_chapter.a['href']
    latest_chapter_info.append(latest_chapter_url)
    # print(f"The info with url appended: {latest_chapter_info}")
    new_chapters.appendleft(latest_chapter_info)
    path_to_image = get_comic_image(comic.get_name(), soup, domain_name)
    new_chapters.appendleft(path_to_image)
    old_chapter_number = int(comic.get_latest_chapter())
    next_chapter = latest_chapter
    next_chapter_number = latest_chapter_number
    while(next_chapter_number > old_chapter_number+1):
        try:
            next_chapter = next_chapter.find_next_sibling('li')
            next_chapter_url = next_chapter.a['href']
            next_chapter_info = get_chapter_info(next_chapter)
            next_chapter_info.append(next_chapter_url)
            next_chapter_number = get_chapter_number(next_chapter_info)
            new_chapters.append(next_chapter_info)
        except Exception:
            # It is possible website messed up an upload, resulting in improper naming,
            # no url associated with a chapter, or other errors.
            print("Error occured while looping through chapters")
            break
    comic.set_latest_chapter(str(latest_chapter_number))
    return new_chapters


def get_chapter_url(chapter):
    return chapter.a['href']


def get_chapter_info(html_text: Tag) -> list:
    return html_text.text.strip().replace('\t', '').split('\n')


def get_chapter_number(latest_chapter_info: list):
    return int(re.search(r'\d+', latest_chapter_info[0]).group())


def main():
    pass


if __name__ == "__main__":
    main()
