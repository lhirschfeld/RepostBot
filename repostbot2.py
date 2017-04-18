# Lior Hirschfeld
# RepostBot

# -- Imports --
from custombot import RedditBot
from difflib import SequenceMatcher
from time import sleep
from sklearn import linear_model
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
    while True:
        for sub in subs:
            searchSub(sub, lim, ml)
        repostBot.updateIds()

        if ml:
            repostBot.updateModels()
        sleep(rate)

# Search a sub for words that need to be defined, and define them.
def searchSub(sub, lim, ml):
    subreddit = r.subreddit(sub)
    for submission in subreddit.hot(limit=lim):
        if submission.id in repostBotids:
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

        results = jargonBot.r.subreddit(sub).search(subTitle)
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
                    textSim = similar(text.selftext, subText)
                except AttributeError:
                    continue
                    if ml:
                        # If ML, after basic checks, predict using the model
                        # to decide whether to reply.
                        if sub not in jargonBot.models:
                            jargonBot.models[sub] = (linear_model.LogisticRegression(), 1)
                            jargonBot.models[sub][0].fit([[1, 1, 1000]], [1])

                        info = {"titleSim": titleSim, "textSim": textSim,
                        "cLength", len(subText), "sID": submission.id, "sub": sub}

                        if random.random() < jargonBot.models[sub][1]:
                            reply(com, word, ml, info=info)
                        elif jargonBot.models[sub][0].predict([[titleSim,
                                textSim, info["cLength"]]]) > 0.8:
                                reply(com, word, ml, info=info)

                    elif similar(result.selftext, subText) > 0.95:
                        reply(submission, result, ml)
                        break

# Reply to a comment with a word definition.
def reply(sub, original, ml, info=None):
    print("Found Submission:", sub.id, sub.title)
    reply = "Beep boop. I am the repost police bot. "
    reply += "I have detected that this is a repost. The original post can"
    reply += " be found [here](" + original.url + ")."
    reply += "\n\n---------\n\n^Check ^out ^my ^[code](https://github.com/lhirschfeld/RepostBot)
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
        print("Hit rate limit error.")
        repostBot.updateIds()
        sleep(600)

repost(50, 10, ["test"])