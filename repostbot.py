# Lior Hirschfeld
# RepostBot

# -- Imports --

import praw


# -- Setup Variables --
r = praw.Reddit('repostBot')
stemmer = PorterStemmer()
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
    subWords = [pair[0] for pair in languages[sub].most_common(10000)]
    for submission in subreddit.hot(limit=lim):
        ids.append(sub.id)

# Reply to a comment with a word definition.
def reply(sub, word, ml, info=None):
    global responses
    print("Found Submission:" + sub.id)
    reply = ""
    try:
        cID = com.reply(reply)

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

repost(50, 10, ["test"], ml=True)
