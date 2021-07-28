# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
#            pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1

class NewsStory (object):
    
    def __init__(self, guid, title, description, link, pubdate):
        
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate
        
    def get_guid(self):
        return self.guid
    
    def get_title(self):
        return self.title
        
    def get_description(self):
        return self.description
    
    def get_link(self):
        return self.link
    
    def get_pubdate(self):
        return self.pubdate


#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS

# Problem 2
class PhraseTrigger(Trigger):
    
    def __init__(self, phrase):
        self.phrase = phrase.lower()
    
    def is_phrase_in(self, phrase):
        """
        Takes in one phrase (string) argument text.
        Returns ​True​ if the whole phrase passed as an argument is present in 
        the text, ​False​ otherwise. This method should not be case-sensitive.
        """
        
        phrase1 = phrase.lower() #phrase passed on as an argument to this function
        phrase2 = self.phrase #phrase stored in the data attributes when this class or a subclass is instantiated
        
        punc = string.punctuation
        
        for e in punc:
            phrase1 = phrase1.replace(e,' ')
        
        list_nopunc = phrase1.split()
        
        list_text = phrase2.split()
        
        for i in range(len(list_nopunc)):
            if list_text[0] == list_nopunc[i]:
                n = 1
                count = 1
                while n < len(list_text) and i + n < len(list_nopunc):
                    if list_text[n] == list_nopunc[i+n]:
                        count += 1
                    n += 1
                if count == len(list_text):
                    return True
            
        return False
        
        
        
        

# Problem 3
        
class TitleTrigger(PhraseTrigger):
    
    def __init__(self,phrase):
        PhraseTrigger.__init__(self, phrase)
    
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        title = story.get_title()
        
        return self.is_phrase_in(title)

# Problem 4
class DescriptionTrigger(PhraseTrigger):
    
    def __init__(self,phrase):
        PhraseTrigger.__init__(self, phrase)
    
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        description = story.get_description()
        
        return self.is_phrase_in(description)


# TIME TRIGGERS

# Problem 5
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.

class TimeTrigger(Trigger):
    
    def __init__(self,time):
        
        try:
            self.time = datetime.strptime(time, "%d %b %Y %H:%M:%S")
            self.time.replace(tzinfo=pytz.timezone("GMT"))
#            self.time = self.time.astimezone(pytz.timezone('EST'))
#            self.time.replace(tzinfo=None)
        except ValueError:
            self.time = datetime.strptime(time, "%d %b %Y %H:%M:%S")





# Problem 6
class BeforeTrigger(TimeTrigger):
    
    def __init__(self, time):
        TimeTrigger.__init__(self, time)
    
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        return story.get_pubdate() < self.time

class AfterTrigger(TimeTrigger):
    
    def __init__(self, time):
        TimeTrigger.__init__(self, time)
    
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        return story.get_pubdate() > self.time

# COMPOSITE TRIGGERS

# Problem 7
class NotTrigger(Trigger):
    
    def __init__(self, trigger):
        self.trigger = trigger
        
    def evaluate(self, story):
        """
        Given a trigger ​T​ and a news item ​x​, the output of the NOT trigger's 
        evaluate method should be equivalent to ​not T.evaluate(x)
        """
        return not self.trigger.evaluate(story)
        
        
# Problem 8
class AndTrigger(Trigger):
    
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
        
    def evaluate(self, story):
        """
        This trigger should take two triggers as arguments to its constructor, 
        and should fire on a news story only if ​both of the inputted triggers
        would fire on that item.
        """
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)

# Problem 9
class OrTrigger(Trigger):
    
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
        
    def evaluate(self, story):
        """
        This trigger should take two triggers as arguments to its constructor, 
        and should fire if either one (or both) of its inputted triggers would 
        fire on that item.
        """
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)


#======================
# Filtering
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    
    filtered_stories = []
    
    for i in stories:
        for j in triggerlist:
            if j.evaluate(i):
                filtered_stories.append(i)
    
    
    return filtered_stories



#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)
    
    def trigger_helper(type_trigger, args):
        
        if type_trigger == 'TITLE':
            return TitleTrigger(args[0])
        elif type_trigger == 'DESCRIPTION':
            return DescriptionTrigger(args[0])
        elif type_trigger == 'AFTER':
            return AfterTrigger(args[0])
        elif type_trigger == 'BEFORE':
            return BeforeTrigger(args[0])
        elif type_trigger == 'NOT':
            return NotTrigger(args[0])
        elif type_trigger == 'AND':
            return AndTrigger(args[0],args[1])
        elif type_trigger == 'OR':
            return OrTrigger(args[0],args[1])
                
    
    # line is the list of lines that you need to parse and for which you need
    # to build triggers
    
    dict_triggers = {}
    
    trigger_list = []
    
    def get_trigger(string):
        return dict_triggers[string]
    
    for i in range(len(lines)):
        line = lines[i].split(',')
#        print(line)
        if line[0] == 'ADD':
            n = 1
            while n < len(line):
                trigger_list.append(get_trigger(line[n]))
                n += 1
        else:
            type_trigger = line[1]
            if type_trigger == ('AND' or 'OR'):
                args = (line[2],line[3])
            else:
                args = (line[2],)
            dict_triggers[line[0]] = trigger_helper(type_trigger,args)
            
    return trigger_list

read_trigger_config('triggers.txt')

SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("Trump")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Clinton")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1]

        # Problem 11
        triggerlist = read_trigger_config('triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.yahoo.com/rss/topstories"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()

