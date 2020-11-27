# async-movies-server
This is the client-server application based on asyncio. It has its own 
protocol for handling sending and receiving messages. This protocol 
accepts text, json, and binary request. The server is connected 
to the database and can respond with data queried from the 
database.

The application is based on:
* asyncio
* asyncpg
* sqlalchemy

## Design goals

- [x] Creation of the server and client
- [x] Creation of the protocol for handling sending messages (message_stream)
- [x] Creation of the tool for handling request (request_manager)
- [x] Creation of the database manager (db_manager)
- [x] Creation of the methods which queries the database (db_manager)
