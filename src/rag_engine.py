from sentence_transformers import SentenceTransformer
import json


# 1. Load the AI embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# 2. Load parking rules from JSON
with open("data/parking_rules.json", "r") as file:
    parking_rules = json.load(file)


# 3. Create searchable text for every rule
rule_texts = []

for rule in parking_rules:

    text = (
        rule["title"]
        + ". "
        + rule["description"]
        + " "
        + " ".join(rule["keywords"])
    )

    rule_texts.append(text)


# 4. Convert parking rules into embeddings
rule_embeddings = model.encode(
    rule_texts,
    convert_to_tensor=True
)


# 5. Find the most relevant parking rule
def find_best_rule(user_input):

    question = user_input.lower()

    # Step 1: Calculate semantic similarity
    question_embedding = model.encode(
        user_input,
        convert_to_tensor=True
    )

    similarities = model.similarity(
        question_embedding,
        rule_embeddings
    )[0]

    # Step 2: Check exact keyword matches
    keyword_matches = []

    for i, rule in enumerate(parking_rules):
        for keyword in rule["keywords"]:

            if keyword.lower() in question:
                keyword_matches.append(
                    (len(keyword), i)
                )

    # Step 3: Give priority to the most specific keyword
    if keyword_matches:

        keyword_matches.sort(reverse=True)

        best_index = keyword_matches[0][1]

    else:
        # Step 4: Use semantic similarity as fallback
        best_index = similarities.argmax().item()

    best_rule = parking_rules[best_index]

    score = similarities[best_index].item()

    return best_rule, score