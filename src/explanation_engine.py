def generate_explanation(user_question, rule):

    title = rule["title"]
    severity = rule["severity"]
    description = rule["description"]

    explanation = f"""
Based on the parking situation you described, the most relevant
parking rule is "{title}".

Why this may be a violation:
{description}

Severity:
{severity}

What you can do:
"""

    for step in rule["resolution"]:
        explanation += f"\n• {step}"

    explanation += """

This explanation is generated using the parking rule retrieved
from the system's knowledge base. Actual parking procedures may
depend on the applicable local authority.
"""

    return explanation