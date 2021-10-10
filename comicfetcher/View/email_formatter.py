from yattag import Doc
from collections import deque
import os
from View import email
doc, tag, text, line = Doc().ttl()
# One-time run, append the New Chapter header to output html
with open('View/html_templates/intro.html', 'r', encoding='utf-8') as f:
    intro = f.read()

with open('View/html_templates/pre_image.html', 'r', encoding='utf-8') as f:
    pre_image_html = f.read()

with open('View/html_templates/post_image.html', 'r', encoding='utf-8') as f:
    post_image_html = f.read()

with open('View/html_templates/post_name.html', 'r', encoding='utf-8') as f:
    post_name_html = f.read()

with open('View/html_templates/post_chapters.html', 'r', encoding='utf-8') as f:
    post_chapter_html = f.read()

with open('View/html_templates/banner.html', 'r', encoding='utf-8') as f:
    banner_html = f.read()

with open('View/html_templates/closer.html', 'r', encoding='utf-8') as f:
    closer_html = f.read()

doc.asis(intro)

def format_chapter(new_chapters: deque, comic_name: str):
    doc.asis(pre_image_html)
    # In case of None, the image is simply assigned a source of None
    doc.stag('img', alt='Cover Image', src=str(new_chapters.popleft()), style="display: block; height: auto; border: 0; width: 220px; max-width: 100%;", width="368")
    doc.asis(post_image_html)
    with tag('strong'):
        text(comic_name)
    doc.asis(post_name_html)
    for i in range(len(new_chapters)):
        # TODO: Can't have Nones in deque, need to fix returns in model
        chapter_info = new_chapters.popleft()
        with tag('p', style="margin: 0; font-size: medium; text-align: center;"):
            with tag('a', href=str(chapter_info[2]), style="color:white"):
                text(chapter_info[0])
            text(" " + str(chapter_info[1]))
    
    doc.asis(post_chapter_html)
    doc.asis(banner_html)

def attach_closer():
    doc.asis(closer_html)
    email.send_email(doc.getvalue())

