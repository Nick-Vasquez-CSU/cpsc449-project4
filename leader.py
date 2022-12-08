
import dataclasses

import redis


# Necessary quart imports

from quart import Quart, request

from quart_schema import QuartSchema, validate_request


app = Quart(__name__)

QuartSchema(app)


# Initialize redis client

redisClient = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)


@dataclasses.dataclass

class LeaderInfo:

    result: str

    guesses: int

# Results endpoint

@app.route("/results/", methods=["POST"])

@validate_request(LeaderInfo)

async def Results(data: LeaderInfo):

    auth = request.authorization

    if auth and auth.username and auth.password:

        leaderboardData = dataclasses.asdict(data)

        score = 0
        count = 1
        if leaderboardData["result"] == "Win":

            if leaderboardData["guesses"] == 1:
                score = 6
            elif leaderboardData["guesses"] == 2:
                score = 5
            elif leaderboardData["guesses"] == 3:
                score = 4
            elif leaderboardData["guesses"] == 4:
                score = 3
            elif leaderboardData["guesses"] == 5:
                score = 2
            elif leaderboardData["guesses"] == 6:
                score = 1
            else:
                return {"Error": "Invalid Guesses."}, 404
        elif leaderboardData["result"] == "Loss":
            score = 0
        else:
            return {"Error": "Invalid Result."}, 404

        if redisClient.hget('leaderboard', 'username') == auth.username:
            score = int(redisClient.hget('leaderboard', 'score')) + score
            count = int(redisClient.hget('leaderboard', 'gamecount')) + count
            averageScore = score / count

            result = redisClient.hset('leaderboard', 'averageScore', averageScore)
            result = redisClient.hset('leaderboard', 'result',leaderboardData["result"])
            result = redisClient.hset('leaderboard', 'guesses',leaderboardData["guesses"])
            result = redisClient.hset('leaderboard', 'score', score)
            result = redisClient.hset('leaderboard', 'gamecount', count)
            result2 = redisClient.zadd("Wordle Leaderboard", {auth.username: averageScore})


        else:

            result = redisClient.hset('leaderboard', 'username' , auth.username)
            result = redisClient.hset('leaderboard', 'averageScore', score)
            result = redisClient.hset('leaderboard', 'result',leaderboardData["result"])
            result = redisClient.hset('leaderboard', 'guesses',leaderboardData["guesses"])
            result = redisClient.hset('leaderboard', 'score', score)
            result = redisClient.hset('leaderboard', 'gamecount', count)
            result2 = redisClient.zadd("Wordle Leaderboard", {auth.username: score})


        return redisClient.hgetall('leaderboard'), 200

    else:
        return (
            {"error": "User not verified"},
            401,
            {"WWW-Authenticate": 'Basic realm = "Login required"'},
        )


@app.route("/top10scores/", methods=["GET"])

async def top10Scores():


    topScores = redisClient.zrange("Wordle Leaderboard", 0, 9, desc = True, withscores = True)


    if topScores != []:

        return ('\n'.join(map(str, topScores))), 200

    else:

        return {"Error": "No data in Database."}, 404
