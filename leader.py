
import dataclasses

import redis
import httpx
import socket
import os
import json
from time import sleep
# Necessary quart imports

from quart import Quart, request

from quart_schema import QuartSchema, validate_request


app = Quart(__name__)
QuartSchema(app)
res = None
#while res is None:
#    try:
#        res = httpx.post("http://"+socket.getfqdn("127.0.0.1:5200/fullsend"))
#        print(res)
#    Get url and put into socket     res =
#    except httpx.RequestError:
#        print("Retrying httpx in 5 seconds...")
#        sleep(5)


# Initialize redis client

redisClient = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)


@dataclasses.dataclass

class LeaderInfo:

    result: str

    guesses: int

# Results endpoint

@app.route("/results", methods=["POST"])

#@validate_request(LeaderInfo)

async def Results():

#    auth = request.authorization

#    if auth and auth.username and auth.password:
#    leaderboardData = dataclasses.asdict(data)
    data = await request.get_json()
    userL = data["user"]
    guessL = data["guesses"]
    statusL = data["status"]
    print(data)

    score = 0
    count = 1
    if statusL == "Win":

        if guessL == 1:
            score = 6
        elif guessL == 2:
            score = 5
        elif guessL == 3:
            score = 4
        elif guessL == 4:
            score = 3
        elif guessL == 5:
            score = 2
        elif guessL == 6:
            score = 1
        else:
            return {"Error": "Invalid Guesses."}, 404
    elif statusL == "Loss":
        score = 0
    else:
        return {"Error": "Invalid Result."}, 404

    if redisClient.hget('leaderboard', 'username') == userL:
        score = int(redisClient.hget('leaderboard', 'score')) + score
        count = int(redisClient.hget('leaderboard', 'gamecount')) + count
        averageScore = score / count

        result = redisClient.hset('leaderboard', 'averageScore', averageScore)
        result = redisClient.hset('leaderboard', 'result',statusL)
        result = redisClient.hset('leaderboard', 'guesses',guessL)
        result = redisClient.hset('leaderboard', 'score', score)
        result = redisClient.hset('leaderboard', 'gamecount', count)
        result2 = redisClient.zadd("Wordle Leaderboard", {userL: averageScore})


    else:

        result = redisClient.hset('leaderboard', 'username' , userL)
        result = redisClient.hset('leaderboard', 'averageScore', score)
        result = redisClient.hset('leaderboard', 'result',statusL)
        result = redisClient.hset('leaderboard', 'guesses',guessL)
        result = redisClient.hset('leaderboard', 'score', score)
        result = redisClient.hset('leaderboard', 'gamecount', count)
        result2 = redisClient.zadd("Wordle Leaderboard", {userL: score})


    return redisClient.hgetall('leaderboard'), 200

#    else:
#        return (
#            {"error": "User not verified"},
#            401,
#            {"WWW-Authenticate": 'Basic realm = "Login required"'},
#        )


@app.route("/top10scores/", methods=["GET"])

async def top10Scores():


    topScores = redisClient.zrange("Wordle Leaderboard", 0, 9, desc = True, withscores = True)


    if topScores != []:

        return ('\n'.join(map(str, topScores))), 200

    else:

        return {"Error": "No data in Database."}, 404
