""" Creates and connects the client with the server,
    after that it sends the specified request to the server. """

from async_client import AsyncClient

HOST = "127.0.0.1"
PORT = 12345


if __name__ == "__main__":
    # test_message = "actor, John Travolta"
    test_message = """
    custom,
    SELECT title, release_date FROM movies_metadata movies
    INNER JOIN movie_metadata_association association ON association.movies_metadata = movies.id
    INNER JOIN genres ON genres.id = association.genres
    INNER JOIN characters ON characters.movie_id = movies.id
    INNER JOIN actors ON actors.id = characters.actor_id
    WHERE actors.name = 'John Travolta'
    AND genres.name = 'Thriller';
    """
    async_client = AsyncClient(
        HOST, PORT, test_request=test_message, test_content_type="text"
    )
    header, answer = async_client.run_client()
    print("header:", header)
    print("answer:", answer)
    async_client.close()
