#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  TweetSnooper.py
#  
#  Copyright 2017 Keaton Brown <linux.keaton@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

########################################################################
#                                                                      #
#    Functions                                                         #
#                                                                      #
########################################################################

def loadCreds(myPath):
    """
    loads the config file, if anything is empty, cause panic
    """
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config.read(myPath+"credentials.ini")
    if not config.sections():
        raise Exception
    for item in config.sections():
        if not [thing[1] for thing in config[item].items()]:
            raise Exception
    return config

def makeCreds(myPath):
    print("Either this is the first time this script is being run, or there "
          "was an error reading the config file. You will now be walked "
          "through obtaining all the credentials this bot needs in order "
          "to function.")
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option
    print("First, we will deal with Reddit.")
    input("Press enter to continue...\n==> ")
    ############################################################# Reddit
    print(" 1) Go to https://www.reddit.com/prefs/apps and sign in with your "
          "bot account. The bot must have moderator privileges.\n"
          " 2) Press the 'create app' button, then enter the following :\n\n"
          "    Name: TweetSnooper (or another name if you so wish)\n"
          "    App type: script\n"
          "    description: Twitter updates for /r/SUBREDDIT\n"
          "                 (or, leave this blank)\n"
          "    about url: https://github.com/WolfgangAxel/TweetSnooper\n"
          "    redirect url: http://127.0.0.1:65010/authorize_callback\n\n"
          " 3) Finally, press the 'create app' button.")
    input("Press enter to continue...\n==> ")
    print("Underneath the name of the app, there should be a string of letters and numbers.\n"
          "That is the bot's client-id.\n"
          "The bot's secret is displayed in the table.")
    redCreds = {}
    for short,thing in [["u","username"],["p","password"],["c","client-id"],["s","secret"]]:
        while True:
            value = input("Please enter the bot's "+thing+":\n==> ")
            confirm = input("Is '"+value+"' correct? (y/n)\n==> ")
            if confirm.lower() == "y":
                redCreds[short] = value
                break
            print("Confirmation failed. Restarting entry")
    print("Now, we will deal with Twitter.")
    input("Press enter to continue...\n==> ")
    ############################################################ Twitter    
    print(" 1) Go to https://apps.twitter.com and sign in with your bot account.\n"
          " 2) Press the 'Create New App' button, then enter the following:\n\n"
          "    Name: TweetSnooper (or another name if you so wish)\n"
          "    Description: A reddit/twitter bot that copies tweets to reddit (or whatever)\n"
          "    Website: https://github.com/WolfgangAxel/TweetSnooper\n"
          "    Callback URL: http://127.0.0.1:65010/authorize_callback\n\n"
          " 3) Accept the agreement and press the 'Create your Twitter application' button")
    input("Press enter to continue...\n==> ")
    print("Go to the 'Keys and Access Tokens' tab.\n"
          "Scroll down and press the 'Create my access token' button.\n"
          "All items are labeled on the screen.")
    twtCreds = {}
    for short,thing in [["ck","consumer key"],["cs","consumer secret"],["at","access token"],["as","access token secret"]]:
        while True:
            value = input("Please enter the bot's "+thing+":\n==> ")
            confirm = input("Is '"+value+"' correct? (y/n)\n==> ")
            if confirm.lower() == "y":
                twtCreds[short] = value
                break
            print("Confirmation failed. Restarting entry")
    print("Almost done! Just a few more items to define.")
    ############################################################### Misc
    mscCreds = {}
    for variable,question in [ ["mySub","Enter the name of your subreddit."],
                               ["botMaster","Enter your personal Reddit username. (This is used for Reddit's user-agent, nothing more)"],
                               ["tweetLimit","How many tweets to keep in the sidebar?"],
                               ["retweets","Would you like retweets and replies to appear in the feed? (y/n)"],
                               ["sleepTime","How many seconds to wait between refreshing? (Use whole numbers like 300 or expressions like 5 * 60)"]
                             ]:
        while True:
            value = input(question+"\n==>")
            confirm = input("Is '"+value+"' correct? (y/n)\n==> ")
            if confirm.lower() == "y":
                mscCreds[variable] = value
                break
            print("Confirmation failed. Restarting entry.")
    print("Now we'll define which Twitter users to pull tweets from.")
    users = []
    while True:
        print("Current list of users:")
        for user in users:
            print("  "+user)
        name = input("Enter the twitter handle of a user you want in your sidebar:\n==> @")
        confirm = input("Add @"+name+"'s tweets to the sidebar? (y/n)\n==> ")
        if confirm.lower() == "y":
            users.append("@"+name)
        else:
            print("@"+name+" was not added to the list.")
        again = input("Add another user? (y/n)\==> ")
        if again.lower() == "n":
            if users != []:
                mscCreds["users"]=str(users)
                break
            else:
                print("No users found. Please add at least one user.")
        else:
            print("Adding another")
    
    config["R"] = redCreds
    config["T"] = twtCreds
    config["M"] = mscCreds
    with open(myPath+"credentials.ini","w") as cfg:
        config.write(cfg)
    print("Config file written successfully")
    return config

def fakeTimeline(users):
    """
    Get tweets from all users, sort them by date, then only return the
    number of them you want (tweetLimit)
    """
    conglomeration = []
    for user in users:
        tweets = T.user_timeline(user,count=tweetLimit)
        for tweet in tweets:
            if retweets == "n" and (tweet.is_quote_status or tweet.in_reply_to_screen_name):
                continue
            conglomeration.append( {"time":tweet.created_at.__str__(), 
                                    "author":tweet.author.name, 
                                    "handle":tweet.author.screen_name, 
                                    "text":tweet.text, 
                                    "link":"https://twitter.com/i/web/status/"+tweet.id_str} )
        # Be nice-ish to Twitter's servers
        time.sleep(1)
    return sorted(conglomeration,key=lambda t: t["time"])[::-1][:tweetLimit]

########################################################################
#                                                                      #
#    Script Startup                                                    #
#                                                                      #
########################################################################

myPath = __file__.replace("TweetSnooper.py","")

try:
    mod = "tweepy"
    import tweepy
    mod = "praw"
    import praw
    mod = "configparser"
    import configparser
    mod = "re"
    import re
    mod = "time"
    import time
except:
    exit(mod+" was not found. Install "+mod+" with pip to continue.")

try:
    creds = loadCreds(myPath)
except:
    creds = makeCreds(myPath)

for variable in creds["M"]:
    exec(variable+' = creds["M"]["'+variable+'"]')
users = eval(users)
tweetLimit = eval(tweetLimit)
sleepTime = eval(sleepTime)
if retweets.lower() not in ["y","n"]:
    retweets = "n"
    print("Error reading retweets variable. Defaulted to 'no'. Ensure "
          "the `retweets` variable in your `credentials.ini` file is "
          "set to either 'y' or 'n' to prevent this warning next time.")

## Twitter authentication
auth = tweepy.OAuthHandler(creds["T"]["ck"],creds["T"]["cs"])
auth.set_access_token(creds["T"]["at"],creds["T"]["as"])
T = tweepy.API(auth)

## Reddit authentication
R = praw.Reddit(client_id = creds["R"]["c"],
                client_secret = creds["R"]["s"],
                password = creds["R"]["p"],
                user_agent = "TweetSnooper, pushing tweets into /r/"+mySub.replace("/r/","").replace("r/","")+"; hosted by /u/"+botMaster.replace("/u/","").replace("u/",""),
                username = creds["R"]["u"].replace("/u/","").replace("u/",""))

## Sidebar creation
sub = R.subreddit(mySub)
print("Bots loaded successfully. Entering main loop...")
while True:
    sidebar = sub.description
    try:
        try:
            parsed = re.search("(.*)\n\n[*]*\n\n##Twitter Feed\n\n(.*)",sidebar,flags=re.DOTALL)
            preFeed = parsed.group(1)+"\n\n****\n\n##Twitter Feed\n\n"
        except:
            print("preFeed failure. Assuming bottom attachment.")
            preFeed = sidebar+"\n\n****\n\n##Twitter Feed\n\n"
        try:
            parsed = re.search(".*\n\n[*]*\n\n##Twitter Feed\n\n.*[*]*(.*)",sidebar,flags=re.DOTALL)
            postFeed = "****"+parsed.group(1)
        except:
            print("postFeed failure")
            postFeed = "****"
        tweetFeed = ""
        for tweet in fakeTimeline(users):
            tweetFeed += tweet["author"]+" ([@"+tweet["handle"]+"]("+tweet["link"]+")): "+tweet["text"]+"\n\n"
        if sidebar != preFeed+tweetFeed+postFeed:
            sub.mod.update(description=preFeed+tweetFeed+postFeed)
            print(time.strftime("%D, %H:%M-\n    ")+"Sidebar was updated")
        time.sleep(sleepTime)
    except Exception as e:
        print("Fatal error:"+str(e.args)+"\nTrying again in one minute")
        time.sleep(60)
    
