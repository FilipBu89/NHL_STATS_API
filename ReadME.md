NHL - Top Scorers - Stats [still in progress]
-
Just playing around and leveraging *https://statsapi.web.nhl.com/* API using few interesting techniques for 
parsing and handling requests and database operations.

Not only data from APIs endpoints is handled concurrently using asyncio library, but also database transactions can be
handled concurrently with help of asyncpg for pooling.