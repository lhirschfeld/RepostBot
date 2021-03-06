# Lior Hirschfeld
# RepostBot

# -- Imports --
import praw

from custombot import RedditBot
from difflib import SequenceMatcher
from time import sleep
from sklearn import linear_model
from math import exp
from datetime import datetime
import random
# -- Setup Variables --
repostBot = RedditBot('repostBot')
responses = []

# -- Methods --

# Check if two strings are similar
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def repost(lim, rate, subs, ml=False):
    searchReddit(lim, rate, subs, ml)

# Search Reddit for words that need to be defined, and define them.
def searchReddit(lim, rate, subs, ml):
        for sub in subs:
            searchSub(sub, lim, ml)
        repostBot.updateIds()

        if ml:
            repostBot.updateModels(["titleSim", "textSim", "cLength"])
        sleep(rate)

# Search a sub for words that need to be defined, and define them.
def searchSub(sub, lim, ml):
    subreddit = repostBot.r.subreddit(sub)
    for submission in subreddit.hot(limit=lim):
        if submission.id in repostBot.ids:
            continue
        repostBot.ids.append(submission.id)
        subTitle = submission.title
        try:
            subText = submission.selftext
            subURL = None
        except AttributeError:
            subText = None
            subURL = submission.url

        # Check if the text of the string is long enough to make a comparison.
        if subText:
            if len(subText) < 100:
                continue

        results = repostBot.r.subreddit(sub).search(subTitle)
        try:
            for result in results:
                # Only check submissions that were submitted before what is being
                # searched.
                # TODO: Figure out how to best approach the problem - very similar
                # post from three months ago, slighly less similar post from a
                # year ago.
                if result.id == submission.id:
                    continue
                elif result.created >= submission.created:
                    continue
                elif subURL:
                    try:
                        if result.URL == subURL:
                            reply(submission, original, ml)
                            break
                    except AttributeError:
                        continue
                elif subText:
                    try:
                        titleSim = similar(result.title, subTitle)
                        textSim = similar(result.selftext, subText)
                    except AttributeError:
                        continue
                    if ml:
                        # If ML, after basic checks, predict using the model
                        # to decide whether to reply.
                        print("Entered ml section...", end="")
                        if sub not in repostBot.models:
                            repostBot.createModel(sub, [[[1, 1, 1000]], [60]])

                        info = {"titleSim": titleSim, "textSim": textSim,
                        "cLength": len(subText), "sID": submission.id, "sub": sub}

                        prediction = repostBot.models[sub][0].predict([[titleSim,
                                textSim, info["cLength"]]])
                        info["prediction"] = prediction
                        print("Random change is", repostBot.models[sub][1]*100, "%")
                        if random.random() < repostBot.models[sub][1]:
                            reply(submission, result, ml, info=info)
                            break
                        elif repostBot.models[sub][0].predict([[titleSim,
                                textSim, info["cLength"]]]) > 10:
                            reply(submission, result, ml, info=info)
                            break

                    elif similar(result.selftext, subText) > 0.8:
                        reply(submission, result, ml)
                        break
        except AttributeError as e:
            print(e)
            # continue

# Reply to a comment with a word definition.
def reply(sub, original, ml, info=None):
    reply = "I have detected"

    if ml and "prediction" in info:
        certainty = 1.0 / (1 + exp((100 - info["prediction"])/100))
        reply += ", with " + str(certainty * 100) + "% certainty,"

    reply += " that this is a repost. The original post can"
    reply += " be found [here](" + original.url + ")."
    if ml:
            reply += """\n\nI am a bot which attempts to find reposts automatically. I use machine learning to do this, and I can use your feedback to improve. Feel free to leave a comment to let me know what you thought!"""
    reply += "\n\n---------\n\n^Check ^out ^my ^[code](https://github.com/lhirschfeld/RepostBot). "
    reply += " ^Please ^contact ^/u/liortulip ^with"
    reply += " ^any ^questions ^or ^concerns."
    try:
        cID = sub.reply(reply)

        if ml:
            info["time"] = datetime.now()
            info["cID"] = cID
            repostBot.responses.append(info)

        print("Replied")
    except praw.exceptions.APIException as error:
        print("Hit rate limit error.", error)
        repostBot.updateIds()
        sleep(600)

while True:
    repost(50, 10, ["funny", "pics", "jokes", "todayilearned", "videos", "aww", "gifs"], ml=True)
    repost(50, 10, ["funny", "pics", "jokes", "todayilearned", "videos", "aww", "gifs"], ml=True)
