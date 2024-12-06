import re
import llm

model = llm.get_model("themodel")

def suggest_predicates_rules(text):
    """Suggests predicates based on keywords and patterns in the text.
    You can select a text at the bottom of this file to use. Feel free to
    modify the rules for your own use case."""
    suggested_predicates = set()

    # Rule 1: Look for common verbs associated with transactions
    transaction_verbs = r"(?:bought|sold_to|sold_object|traded|acquired|consigned|purchased|exported|imported|donated|received|transferred)"
    matches = re.findall(transaction_verbs, text, re.IGNORECASE)
    suggested_predicates.update(matches)

    # Rule 2: Look for verbs indicating collaboration or connection
    collaboration_verbs = r"(?:worked with|partnered with|collaborated with|associated with|connected to|supplied to|met with)"
    matches = re.findall(collaboration_verbs, text, re.IGNORECASE)
    suggested_predicates.update(matches)

    # Rule 3: Look for verbs related to legal actions
    legal_verbs = r"(?:charged with|convicted of|sentenced to|arrested for|investigated for)"
    matches = re.findall(legal_verbs, text, re.IGNORECASE)
    suggested_predicates.update(matches)


    # Rule 4: Look for location words implying operation
    location_verbs = r"(?:operated in|located in|based in|established in)"
    matches = re.findall(location_verbs, text, re.IGNORECASE)
    suggested_predicates.update(matches)


    # Rule 5: Look for ownership and provenance
    ownership_verbs = r"(?:owned by|belonged to|originated from|stolen from|traced to)"
    matches = re.findall(ownership_verbs, text, re.IGNORECASE)
    suggested_predicates.update(matches)

    return list(suggested_predicates)

import llm

def refine_predicates_llm(suggested_predicates, text):
    """Refines the suggested predicates using an LLM."""
    prompt = f"""The following predicates were suggested for extracting relationships from a text about the antiquities trade: {', '.join(suggested_predicates)}.  The text is:  {text}.  Refine this list, removing irrelevant predicates, adding any crucial missing predicates or snake_case descriptive two-word phrases relevant to the antiquities trade (focus on key players, institutions, objects, and transactions), and prioritizing predicates that will illuminate the key aspects of the trade network. Return the refined list as a comma-separated string. Provide a brief rationale."""
    refined_predicates = model.prompt(prompt, temperature=0)
    return refined_predicates

def select_predicates(text):
    """Selects predicates using a hybrid rule-based and LLM approach."""
    initial_suggestions = suggest_predicates_rules(text)
    refined_predicates = refine_predicates_llm(initial_suggestions, text)
    return refined_predicates

text = open("source-texts/39.txt", "r").read() ## this refers to Giacomo Medici
predicates = select_predicates(text)
print(f"Selected Predicates: {predicates}")