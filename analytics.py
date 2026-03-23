def calculate_risk(events):
    score = 0

    for e in events:
        event_type = e[1]

        if event_type == "FAILED_LOGIN":
            score += 2
        elif event_type == "INTRUDER_DETECTED":
            score += 5
        elif event_type == "SUCCESS_LOGIN":
            score -= 1

    # Normalize risk
    if score < 3:
        return "LOW"
    elif score < 7:
        return "MEDIUM"
    else:
        return "HIGH"