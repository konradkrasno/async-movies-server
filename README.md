# async-movies-server
This is client-server application based on asyncio. It has own protocol 
for handling sending and receiving messages. Protocol attends text, json and
binary request. The application is connected with database and can response with 
data queried from database. \
It will be used for receiving the set of recommended 
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
