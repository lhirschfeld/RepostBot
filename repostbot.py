# Lior Hirschfeld
# RepostBot

# -- Imports --

import praw
import pickle
from difflib import SequenceMatcher
from time import sleep

# -- Setup Variables --
r = praw.Reddit('repostBot')
responses = []

with open('ids.pickle', 'rb') as handle:
    try:
        ids = pickle.load(handle)
    except EOFError:
        ids = []

# # Model Takes: [Word Popularity, Word Length, Comment Length]
# # Models is a dictionary with a touple at each key containing:
# # (linear regression, randomness rate)
# with open('models.pickle', 'rb') as handle:
#     try:
#         models = pickle.load(handle)
#     except EOFError:
#         models = {}

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
        with open('ids.pickle', 'wb') as handle:
            pickle.dump(ids, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # if ml:
        #     updateModels()
        sleep(rate)

# # Update the machine learning model and save it.
# def updateModels():
#     global responses, models
#     currentTime = datetime.now()
#     oldResponses = [(currentTime - r["time"]).total_seconds() > 3600
#                              for r in responses]
#     responses = [(currentTime - r["time"]).total_seconds() < 3600
#                              for r in responses]
#     for r in oldResponses:
#         result = 0
#         url = "https://reddit.com/" + r["sID"] + "?comment=" + r["cID"]
#         submission = reddit.get_submission(url=url)
#         comment_queue = submission.comments[:]
#         if comment_queue:
#             com = comment_queue.pop(0)
#             result += com.score
#             comment_queue.extend(com.replies)
#         while comment_queue:
#             com = comment_queue.pop(0)
#             text = TextBlob(com.text)
#             result += text.sentiment.polarity * com.score
#         models[r["sub"]][0].fit([[r["popularity"], r["wLength"], r["cLength"]]],
#                               [result])
#
#         # Update odds of random choice
#         models[r]["sub"][1] *= 0.96
#     with open('models.pickle', 'wb') as handle:
#         pickle.dump(models, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Search a sub for words that need to be defined, and define them.
def searchSub(sub, lim, ml):
    # global models
    subreddit = r.subreddit(sub)
    for submission in subreddit.hot(limit=lim):
        if submission.id in ids:
            continue
        ids.append(submission.id)
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

        results = r.subreddit(sub).search(subTitle)
        for result in results:
            # Only check submissions that were submitted before what is being
            # searched.
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
                    if similar(result.selftext, subText) > 0.95:
                        reply(submission, result, ml)
                        break
                except AttributeError:
                    continue

# Reply to a comment with a word definition.
def reply(sub, original, ml, info=None):
    global responses
    print("Found Submission:", sub.id, sub.title)
    reply = "I have detected that this is a repost. The original post can"
    reply += " be found [here](" + original.url + ")."
    reply += "\n\n---------\n\n^I ^am ^a ^bot. ^Check ^out ^my ^[code](https://github.com/lhirschfeld/RepostBot)
    reply += " ^Please ^contact ^/u/liortulip ^with"
    reply += " ^any ^questions ^or ^concerns."
    try:
        cID = sub.reply(reply)
        # if ml:
        #     info["time"] = datetime.now()
        #     info["cID"] = cID
        #     responses.append(info)
        print("Replied")
    except praw.exceptions.APIException as error:
        print("Hit rate limit error.")
        with open('ids.pickle', 'wb') as handle:
            pickle.dump(ids, handle, protocol=pickle.HIGHEST_PROTOCOL)
        sleep(600)

repost(50, 10, ["test"])
