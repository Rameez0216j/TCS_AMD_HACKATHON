from src.components.agents.graph import graph


def main():

    state = {
        "transaction": sample_transaction,
        "iteration_count": 0,
        "confidence_score": 0,
        "messages": [],
    }

    result = graph.invoke(state)

    print(result)


if __name__ == "__main__":
    main()
