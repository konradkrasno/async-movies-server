# async-movies-server
This is the client-server application based on asyncio. It has its own 
protocol for handling sending and receiving messages. This protocol 
attends text, json, and binary request. The application is connected 
to the database. The server can respond with data queried from the 
database. \
The application will be used for sending the set of the recommended 
movies based on given movies.

The application is based on:
* asyncio
* asyncpg
* sqlalchemy

## Design goals

- [x] Creation of the server and client
- [x] Creation of the protocol for handling sending messages (message_stream)
- [x] Creation of the tool for handling request (request_manager)
- [ ] Creation of the database manager (db_manager)
- [ ] Write queries to the database.
