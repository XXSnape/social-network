"""
Модуль с фикстурами.
"""

from hashlib import sha256

GOOD_RESULT = {"result": True}

BAD_TOKEN = "bad-token"

AUTHORIZATION_ERROR = {
    "result": False,
    "error_type": "HTTPException",
    "error_messages": "Authorization error.",
}

USER = {
    "result": True,
    "user": {
        "id": 1,
        "name": "user1",
        "followers": [],
        "following": [],
    },
}

FOLLOWERS = [
    {"user_id": 2, "follower_id": 1},
    {"user_id": 1, "follower_id": 2},
    {"user_id": 3, "follower_id": 1},
]

USERS = [
    {"id": 1, "token": sha256(b"test").hexdigest()},
    {"id": 2, "token": sha256(b"test2").hexdigest()},
    {"id": 3, "token": sha256(b"test3").hexdigest()},
    {"id": 4, "token": sha256(b"test4").hexdigest()},
]

PROFILE_DATA = {
    "result": True,
    "user": {
        "id": 2,
        "name": "user2",
        "followers": [{"id": 1, "name": "user1"}],
        "following": [{"id": 1, "name": "user1"}],
    },
}

ALL_TWEETS = {"result": True, "tweets": []}

TWEETS = [
    {"content": "tweet1_user1", "user_id": 1},
    {"content": "tweet2_user1", "user_id": 1},
    {"content": "tweet1_user2", "user_id": 2},
]

LIKES = [
    {"tweet_id": 1, "user_id": 1},
    {"tweet_id": 1, "user_id": 2},
    {"tweet_id": 2, "user_id": 3},
]

FOLLOWER = {"id": 2, "name": "user2"}
FOLLOWING = [{"id": 2, "name": "user2"}, {"id": 3, "name": "user3"}]

ADDED_TWEETS = [
    {
        "id": 3,
        "content": "tweet1_user2",
        "attachments": [],
        "author": {"id": 2, "name": "user2"},
        "likes": [],
    },
    {
        "id": 2,
        "content": "tweet2_user1",
        "attachments": [],
        "author": {"id": 1, "name": "user1"},
        "likes": [],
    },
    {
        "id": 1,
        "content": "tweet1_user1",
        "attachments": [],
        "author": {"id": 1, "name": "user1"},
        "likes": [],
    },
]

ADDED_LIKES = [
    {"user_id": 1, "name": "user1"},
    {"user_id": 2, "name": "user2"},
]

LIKE = {"user_id": 3, "name": "user3"}

METHOD_NOT_ALLOWED = {
    "result": False,
    "error_type": "HTTPException",
    "error_messages": "Method Not Allowed",
}
