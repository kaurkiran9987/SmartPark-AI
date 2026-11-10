
# USER AGENT

def user_agent(rule):

    return {
        "agent": "User Agent",

        "finding": (
            f"Your parking situation may relate to "
            f"{rule['title']}."
        ),

        "suggestions": rule["resolution"]
    }


# ENFORCEMENT AGENT

def enforcement_agent(rule):

    return {
        "agent": "Enforcement Agent",

        "finding": (
            f"Retrieved rule: {rule['rule_id']} - "
            f"{rule['title']}"
        ),

        "severity": rule["severity"],

        "checks": [
            "Verify the parking location.",
            "Review the violation details.",
            "Check applicable parking regulations.",
            "Review the official dispute procedure if needed."
        ]
    }
