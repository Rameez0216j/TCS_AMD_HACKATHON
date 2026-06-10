from neo4j import GraphDatabase

URI = "neo4j+ssc://c8168987.databases.neo4j.io"
USERNAME = "c8168987"
PASSWORD = "Rw9dHdY1rV9k-to31oeiUs2wAHiWbTKU2X6-TtvpOYE"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    # Create two test nodes
    session.run("""
        CREATE (:TestNode {id: 1, name: 'Node 1'})
        CREATE (:TestNode {id: 2, name: 'Node 2'})
    """)

    print("✓ Inserted 2 nodes")

    # Verify insertion
    result = session.run("""
        MATCH (n:TestNode)
        RETURN n.id AS id, n.name AS name
    """)

    print("\nNodes in Neo4j:")
    for record in result:
        print(record["id"], "-", record["name"])

driver.close()
