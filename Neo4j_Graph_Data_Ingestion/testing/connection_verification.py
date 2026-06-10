from neo4j import GraphDatabase

URI = "neo4j+ssc://c8168987.databases.neo4j.io"
USERNAME = "c8168987"
PASSWORD = "Rw9dHdY1rV9k-to31oeiUs2wAHiWbTKU2X6-TtvpOYE"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

try:
    driver.verify_connectivity()
    print("CONNECTED")
except Exception as e:
    print(e)

driver.close()


# Check diff btw 'neo4j+ssc://c8168987.databases.neo4j.io' and 'neo4j+s://c8168987.databases.neo4j.io'
