A python application that uses natural language input to generate SQLite query, queries a database, and responds with a natural language answer.

The database for this project includes information on airports, airlines, routes, and planes. Data is obtained from https://openflights.org/data.

## Example
Question:
What are the top 5 busiest airports, and how many incoming and outgoing routes do they have?

Generated SQL Syntax Response:
```sql
SELECT a.name AS airport_name, 
       COUNT(CASE WHEN r.src_airport_id = a.airport_id THEN 1 END) AS outgoing_routes,
       COUNT(CASE WHEN r.dst_airport_id = a.airport_id THEN 1 END) AS incoming_routes
FROM Airport a
JOIN Route r ON a.airport_id = r.src_airport_id OR a.airport_id = r.dst_airport_id
GROUP BY a.airport_id
ORDER BY (outgoing_routes + incoming_routes) DESC
LIMIT 5;
```
 
Query Raw Response:
```sql
[
       ('Hartsfield Jackson Atlanta International Airport', 915, 911),
       ("Chicago O'Hare International Airport", 558, 550),
       ('Beijing Capital International Airport', 535, 534),
       ('London Heathrow Airport', 527, 524),
       ('Charles de Gaulle International Airport', 524, 517)
]
```
 
Natural Language Response:
The top 5 busiest airports, based on the total number of incoming and outgoing routes, are as follows:
1. Hartsfield-Jackson Atlanta International Airport: 915 outgoing routes, 911 incoming routes
2. Chicago O'Hare International Airport: 558 outgoing routes, 550 incoming routes
3. Beijing Capital International Airport: 535 outgoing routes, 534 incoming routes
4. London Heathrow Airport: 527 outgoing routes, 524 incoming routes
5. Charles de Gaulle International Airport: 524 outgoing routes, 517 incoming routes
