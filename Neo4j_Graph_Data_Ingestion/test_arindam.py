from neo4j import GraphDatabase

URI = "neo4j+ssc://8689f3a7.databases.neo4j.io"
USERNAME = "8689f3a7"
PASSWORD = "pExO8vCl3SRYu5qkBtwXxNfvhVIUhcYans_v3fU11wM"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def test_connection():
    with driver.session() as session:
        result = session.run("RETURN 'Connected to Neo4j' AS message")
        for record in result:
            print(record["message"])

test_connection()

driver.close()