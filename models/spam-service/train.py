"""Trains a TF-IDF + LogisticRegression SMS spam classifier and saves
model.pkl + vectorizer.pkl. Two artifacts instead of one — the serving
layer has to load and use both, which is the point of this service in
the demo (not every model ships as a single .pkl).

Dataset is a small embedded sample (not downloaded) so training works
offline and reproducibly. Swap in the full UCI SMS Spam Collection
dataset for a real project.
"""
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

SPAM = [
    "WINNER!! You have been selected to receive a $1000 cash prize. Call now!",
    "URGENT: Your account will be suspended. Click here to verify immediately.",
    "Congratulations! You've won a free iPhone. Claim your prize now!",
    "FREE entry in our weekly draw for a chance to win a brand new car.",
    "You have won a $500 Walmart gift card. Click the link to claim.",
    "Limited time offer! Buy now and get 90% off. Click here before it's gone.",
    "Your loan of $5000 has been approved. Reply YES to receive funds today.",
    "Hot singles in your area want to meet you tonight! Click now.",
    "Congrats! You are pre-approved for a platinum credit card. Apply now.",
    "Claim your free vacation package to the Bahamas, call now to redeem.",
    "URGENT: You have unclaimed lottery winnings, contact us immediately.",
    "Act now! This exclusive deal expires in 1 hour, don't miss out.",
    "You've been chosen for a free trial, no credit card required, click here.",
    "Get rich quick with this one simple trick, banks hate it!",
    "Your package could not be delivered, click here to reschedule with a small fee.",
    "Text STOP to unsubscribe, or WIN to enter our cash giveaway now.",
    "Final notice: your subscription payment failed, update billing now.",
    "You are the lucky winner of our monthly raffle, claim within 24 hours.",
    "Cheap meds online, no prescription needed, order now and save 80%.",
    "Your computer has a virus, call this number immediately for support.",
]

HAM = [
    "Hey, are we still on for lunch tomorrow at noon?",
    "Can you send me the report before end of day please?",
    "Thanks for the birthday wishes, had a great day!",
    "Meeting moved to 3pm, see you in the conference room.",
    "Don't forget to pick up milk on your way home.",
    "The kids' soccer practice got cancelled due to rain.",
    "I finished the assignment, uploading it to the shared drive now.",
    "Let's catch up this weekend, it's been a while.",
    "The flight got delayed by two hours, I'll be there around 9.",
    "Can you review my pull request when you get a chance?",
    "Happy anniversary! Hope you have a wonderful day together.",
    "Reminder: dentist appointment is at 10am on Thursday.",
    "Great job on the presentation today, the team loved it.",
    "I'm running about 10 minutes late, traffic is bad.",
    "Let me know if you need anything else for the trip.",
    "The wifi password is on the fridge if you need it.",
    "Just checking in, how did the interview go?",
    "Dinner's ready whenever you get home.",
    "Can we reschedule our call to Friday morning instead?",
    "Thanks for helping me move last weekend, really appreciate it.",
]

texts = SPAM + HAM
labels = [1] * len(SPAM) + [0] * len(HAM)  # 1 = spam, 0 = ham

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42, stratify=labels
)

vectorizer = TfidfVectorizer(stop_words="english")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test_vec))
print(f"Test accuracy: {accuracy:.3f}")

joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")
print("Saved model.pkl and vectorizer.pkl")
