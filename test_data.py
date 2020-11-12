""" Provides data for testing server and client behaviour. """

valid_data = [
    {
        "message": "hey, what's up?",
        "content_type": "text",
        "encoding": "utf-8",
    },
    {
        "message": {
            "name": "Konrad",
            "message": "Hello world",
        },
        "content_type": "json",
        "encoding": "ascii",
    },
    {
        "message": b"Hello world",
        "content_type": "binary",
        "encoding": "ascii",
    }
]

wrong_data = [
    {
        "message": "hey, what's up?",
        "content_type": "unknown",
        "encoding": "utf-8"
    },
    {
        "message": "Hello world!",
        "content_type": "text",
        "encoding": "unknown",
    },
    {
        "message": b"Hello world",
        "content_type": "json",
        "encoding": "utf-8",
    },
    {
        "message": "Hello world",
        "content_type": "binary",
        "encoding": "utf-8",
    },
    {
        "message": {
            "name": "Konrad",
            "message": "hello",
        },
        "content_type": "text",
        "encoding": "utf-8",
    },
]
