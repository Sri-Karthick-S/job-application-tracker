from sentence_transformers import SentenceTransformer, util

# Load pre-trained model
model = SentenceTransformer('all-mpnet-base-v2')

# Define intent examples
intents = {
    "application_submitted": [
        "We have received your application", "Your application has been submitted", "Resume received successfully"
    ],
    "progression": [
        "Congratulations, you are shortlisted", "You have been selected for the next round", "Interview scheduled"
    ],
    "rejection": [
        "Unfortunately, you were not selected", "We regret to inform you", "Your application was not successful"
    ],
    "offer_received": [
        "Congratulations! We are pleased to offer you", "Your offer letter is attached", "Welcome to the team"
    ],
    "follow_up": [
        "Please confirm your availability", "We need additional details", "Can you provide the requested information"
    ]
}


# Precompute intent embeddings
intent_embeddings = {
    intent: model.encode(phrases, convert_to_tensor=True)
    for intent, phrases in intents.items()
}

def classify_email_subject(subject, intent_embeddings, threshold=0.75):
    """
    Classify the email subject into one of the predefined intents.

    Args:
        subject (str): Email subject line.
        intent_embeddings (dict): Precomputed embeddings for intents.
        threshold (float): Minimum similarity score to assign an intent.

    Returns:
        str: The best matching intent or 'not_job_related' if no match.
        float: Similarity score of the best match.
    """
    # Generate embedding for the email subject
    subject_embedding = model.encode(subject, convert_to_tensor=True)

    best_intent = "not_job_related"
    best_score = 0

    # Compare subject embedding with intent embeddings
    for intent, embeddings in intent_embeddings.items():
        score = util.cos_sim(subject_embedding, embeddings).max().item()
        if score > best_score:
            best_intent = intent
            best_score = score

    # Return the best intent if it meets the threshold
    return (best_intent, best_score) if best_score >= threshold else ("not_job_related", best_score)

# Example email subjects
subjects = [
    "We have received your application for Software Engineer",
    "Congratulations, you are shortlisted for the next round",
    "Unfortunately, you have not been selected for the position",
    "Interview Invitation for the Project Manager Role",
    "Welcome to the team! Your offer letter is attached",
    "Thank you for coming to the family party"
]

# Classify each subject
for subject in subjects:
    intent, score = classify_email_subject(subject, intent_embeddings, threshold=0.6)
    print(f"Subject: {subject}")
    print(f"Intent: {intent}, Similarity Score: {score:.2f}")
    print("-" * 50)

