import requests


def guardrail_check(report):

    response = requests.post("http://localhost:8000/validate", json={"report": report})

    return response.json()


def decision_node(state):

    report = state["reasoning_result"]

    validation = guardrail_check(report)

    state["decision_result"] = {"approved": validation["approved"], "report": report}

    return state
