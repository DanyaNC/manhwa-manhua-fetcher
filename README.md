# Manhwa Manhua Fetcher
Scrapes a user selection of manhwas/manhuas from three websites of scanlation groups (Reaperscans, Asurascans, Flamescans) and emails the user if there are new chapters available for their selected comics, along with the comic's cover image and links to the new chapters.

Sends the user an email with cover images and links to the new chapters for each comic using dynamically written HTML. Hosted using AWS Lambda which calls S3 to host images and data, and SES to send emails. Written in Python using BeautifulSoup4, Requests, Yattag, and Boto3. Deployed using the Serverless framework.

## A standard desktop view output:
https://user-images.githubusercontent.com/6255532/139986573-eb57022c-5111-4632-a27e-f21a353ae1c0.mp4
## A standard mobile view output:
https://user-images.githubusercontent.com/6255532/139986665-c485f88c-f802-46be-8fa3-5506553c95c2.mp4
## An unrealistic absurdly long desktop output:
https://user-images.githubusercontent.com/6255532/139986921-fc5409f5-2f7a-412e-a178-2a87fbfd6f42.mp4
