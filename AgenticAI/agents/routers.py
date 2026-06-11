MAX_ITERATIONS = 2


def confidence_router(state):

    if state["confidence_score"] < 0.80 and state["iteration_count"] < MAX_ITERATIONS:
        return "retry"

    return "approved"
