import pickle
import praw
import random

from textblob import TextBlob
from datetime import datetime
from sklearn import linear_model
class RedditBot:
    """A class that performs basic operations, working with Reddit's
    PRAW API."""

    def __init__(self, botName):
        # Setup the bot and primary variables.

        self.r = praw.Reddit(botName)
        self.responses = []
        with open('ids.pickle', 'rb') as handle:
            try:
                self.ids = pickle.load(handle)
            except EOFError:
                self.ids = []
        with open('models.pickle', 'rb') as handle:
            try:
                self.models = pickle.load(handle)
            except EOFError:
                self.models = {}

    def updateIds(self):
        # Save the new ids of comments that have been responded to.
        with open('ids.pickle', 'wb') as handle:
            pickle.dump(self.ids, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def updateModels(self, modelParams):
        # Model params is a list of strings which contains the keys in
        # each result which should be used to update the model.

        # Models is a dictionary with a touple at each key containing:
        # (linear regression, randomness rate)
        currentTime = datetime.now()
        oldResponses = [(currentTime - r["time"]).total_seconds() > 3600
                                 for r in self.responses]
        self.responses = [(currentTime - r["time"]).total_seconds() < 3600
                                 for r in self.responses]

        for r in oldResponses:
            result = 0
            url = "https://reddit.com/" + r["sID"] + "?comment=" + r["cID"]
            submission = self.r.get_submission(url=url)
            comment_queue = submission.comments[:]

            if comment_queue:
                com = comment_queue.pop(0)
                result += com.score
                comment_queue.extend(com.replies)

            while comment_queue:
                com = comment_queue.pop(0)
                text = TextBlob(com.text)
                result += text.sentiment.polarity * com.score

            x = []

            for key in modelParams:
                x.append(r[key])

            # TODO: Modify fitting so that the model actually remembers its
            # old information.

            self.models[r["sub"]][0].fit([x], [result])

            # Update odds of random choice
            self.models[r]["sub"][1] *= 0.96

        with open('models.pickle', 'wb') as handle:
            pickle.dump(self.models, handle, protocol=pickle.HIGHEST_PROTOCOL)
