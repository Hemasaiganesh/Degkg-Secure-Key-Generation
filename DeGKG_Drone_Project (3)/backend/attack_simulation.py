# attack_simulation.py
import random
import datetime

def simulate_attack():

    # Attack probability model
    attacks = {
        "MITM Attack": 0.25,
        "Replay Attack": 0.20,
        "Sybil Attack": 0.15,
        "Unauthorized Drone Access": 0.15,
        "No Attack": 0.25
    }

    attack_type = random.choices(
        population=list(attacks.keys()),
        weights=list(attacks.values())
    )[0]

    severity_levels = {
        "MITM Attack": "HIGH",
        "Replay Attack": "MEDIUM",
        "Sybil Attack": "HIGH",
        "Unauthorized Drone Access": "CRITICAL",
        "No Attack": "NONE"
    }

    status = "SAFE"
    impact = "System operating normally"

    # Threat score for AI graph
    threat_score_map = {
        "MITM Attack": random.randint(70, 95),
        "Replay Attack": random.randint(40, 70),
        "Sybil Attack": random.randint(75, 98),
        "Unauthorized Drone Access": random.randint(90, 100),
        "No Attack": random.randint(0, 10)
    }

    if attack_type != "No Attack":
        status = random.choices(["BLOCKED", "SUCCESS"], weights=[85, 15])[0]

        if status == "BLOCKED":
            impact = "Attack detected and blocked by DeGKG security mechanism"
        else:
            impact = "SECURITY BREACH! Communication compromised"

    threat_score = threat_score_map[attack_type]

    # Detection confidence
    confidence = random.uniform(0.80, 0.99) if status=="BLOCKED" else random.uniform(0.30, 0.60)
    confidence = round(confidence, 2)

    # Response time in milliseconds
    response_time = round(random.uniform(0.5, 5.0), 3)

    return {
        "attack_type": attack_type,
        "status": status,
        "severity": severity_levels[attack_type],
        "impact": impact,
        "threat_score": threat_score,
        "confidence": confidence,
        "response_time_ms": response_time,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
