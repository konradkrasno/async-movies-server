""" Provides data for testing server and client behaviour. """

valid_data = [
    {
        "message": "custom, SELECT title FROM movies_metadata WHERE title='Pulp Fiction';",
        "content_type": "text",
        "encoding": "utf-8",
        "result": {"answer": [{"title": "Pulp Fiction"}]},
    },
    {
        "message": {
            "category": "custom",
            "query": "SELECT title FROM movies_metadata WHERE title='Pulp Fiction';",
        },
        "content_type": "json",
        "encoding": "ascii",
        "result": {"answer": [{"title": "Pulp Fiction"}]},
    },
    {
        "message": b"Hello world",
        "content_type": "binary",
        "encoding": "ascii",
        "result": {"answer": "Wrong request type. Required type: text or JSON."},
    },
]

wrong_data = [
    {"message": "hey, what's up?", "content_type": "unknown", "encoding": "utf-8"},
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

test_actor_query_result = {
    "answer": [
        {"title": "Three Colors: White"},
        {"title": "What Will You Do When You Catch Me?"},
        {"title": "Jasminum"},
        {"title": "Body"},
        {"title": "The Closed Circuit"},
        {"title": "Happy New York"},
    ]
}
