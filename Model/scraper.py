from bs4 import BeautifulSoup
import lxml
import re
import requests



#Test method for first practicing on a loca file of the website's downloaded html file
# def open_html():
#     with open("C:/Users/Danya/Desktop/SDE/manhwa-manhua-fetcher/Test_HTML-Website/html_test.html", "r") as f:
#         html_file = BeautifulSoup(f, "lxml")
#     return html_file
    
def open_html():
    html_file = requests.get("https://reaperscans.com/series/demonic-emperor/").text
    return html_file



def process_html():
    html_file = open_html()
    
    soup = BeautifulSoup(html_file, "lxml")
    
    latest_chapter = soup.find('li', class_ = 'wp-manga-chapter')

    #Stores 2 strings in a tuple, them being of the format:
    #Chapter ###, indicating the chapter's number,
    #A line stating how long ago the chapter was upload (e.g 30 mins ago, 2 days ago)

    latest_chapter_info : tuple = latest_chapter.text.strip().partition('\n')
    
    #Extract integers from the chapter number string. Use this to check if it is greather than
    #Previously checked number stored in our data.
    latest_chapter_number = int(re.search(r'\d+', latest_chapter_info[0]).group())
    print(latest_chapter_number)
    


def main():
    process_html()


if __name__ == "__main__":
    main()