# test_pytorch_transformers.py
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

def analyze_sentiment(text):
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaForSequenceClassification.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits[0]
    labels = ["NEGATIVE", "NEUTRAL", "POSITIVE"]
    _, predicted_class = torch.max(scores, dim=0)
    return labels[predicted_class]

# Testez l'analyse de sentiment
text = "Bitcoin will increase"
sentiment = analyze_sentiment(text)
print(f"Sentiment: {sentiment}")
