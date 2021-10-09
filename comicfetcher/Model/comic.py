class Comic():

    def __init__(self, info: list):
        self.name = info[0]
        self.latest_chapter = info[1]
        self.url = info[2]

    def get_latest_chapter(self):
        return self.latest_chapter

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def get_csv_dict(self):
        return {'Names': self.name, 'Last_Chapter': self.latest_chapter, 'URL': self.url}

    def set_latest_chapter(self, new_chapter: str):
        self.latest_chapter = new_chapter

    def __str__(self):
        output_string = (f"Name: {self.name}, Latest Chapter: "
                         "{self.latest_chapter}, URL: {self.url}")
        return output_string
