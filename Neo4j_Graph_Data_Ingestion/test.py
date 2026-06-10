from neo4j import GraphDatabase

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+ssc://c8168987.databases.neo4j.io"
AUTH = ("c8168987", "Rw9dHdY1rV9k-to31oeiUs2wAHiWbTKU2X6-TtvpOYE")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()