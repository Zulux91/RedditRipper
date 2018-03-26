#Import Python Reddit API Wrapper
import praw
#Import time to get the latest time
import time
#datetime to do unix/readable translations
import datetime
#We use this for making files and folders
import os
 
#main code
def main():
 
    #Connect API to my APP
    reddit = praw.Reddit(client_id='', client_secret='', password='', user_agent='', username='')
    #ask what sub to archive
    subname = input('Input the subreddit to archive: ')
    #Set subreddit to what the user input
    subreddit = reddit.subreddit(subname)
   
    #Archive an entire subreddit
    archive(subreddit,subname)
 
def archive(subreddit,subname):
    #make a folder named after the subreddit we're archiving if it doesn't currently exist
    if not os.path.exists(subname):
        os.makedirs(subname)
    #get the start date
    date1 = input('Input the start date YYYY/MM/DD: ')
    #make it unix
    date1 = time.mktime(datetime.datetime.strptime(date1, "%Y/%m/%d").timetuple())
    #adds 1 day to the first date - "Get all links from the first day"
    date2 = date1 + 86400
    #enters the directory we just made using the cd class made below
    #outside of the 'with' it goes back to the folder where the script is held
    with cd(subname):
        #loop until the current datetime
        while date2 < time.time():
            #for each submission between the two dates, process them
            for submission in subreddit.submissions(date1,date2):
                process_submission(submission)
            #add a day onto it
            date1+=86400
            date2+=86400
 
#What to do with each submission
def process_submission(submission):
    title = submission.title
    #strip invalid characters from submissions title
    title = title.translate({ord(i):None for i in '/><?:|*"'})
    #translate doesn't work for backslashes lol
    title = title.replace("\\","")
    #strip whitespaces newlines etc
    title = title.strip()
    #Max length is 255 chars in Windows
    title=title[:240]
    #check if it's already archived
    if not os.path.exists(title):
        #print the title to console
        print(title)
        #make a file <post name>.txt if it doesn't already exist
        file = open(title+".txt","w", encoding='utf-8')
        #some metadata
        file.write("ID: "+submission.id+"\n")
        #make a readable date and write to the file
        readabledate = (datetime.datetime.fromtimestamp(int(submission.created)).strftime('%Y-%m-%d %H:%M:%S'))
        file.write("date: "+str(readabledate)+"\n")
        file.write("author: "+submission.author.name+"\n")
        file.write("url: "+submission.url+"\n")
        #write the selftext
        if submission.selftext != "":
            file.write("\n---------------------------------------\n\n")
            file.write(submission.selftext)
        file.write("\n\n---------------------------------------\n\n")
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            readablecommentdate = (datetime.datetime.fromtimestamp(int(comment.created)).strftime('%Y-%m-%d %H:%M:%S'))
            file.write(comment.id+" // ")
            #if the author deleted their account it fails so
            if comment.author != None:
                file.write(comment.author.name)
            file.write(" // "+readablecommentdate+"\n")
            file.write(comment.body+"\n\n")
        file.close()
 
 
#so we can change directories easily
class cd:
    #Context manager for changing the current working directory
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
 
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
 
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
 
#actually run it lol
main()
