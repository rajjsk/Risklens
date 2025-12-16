from transformers import pipeline

class ZeroShotClassifier:
    def __init__(self, model_name="facebook/bart-large-mnli"):
        print("⏳ Loading Zero-Shot model... (first run may take time)")
        self.clf = pipeline(
            "zero-shot-classification",
            model=model_name,
            framework="tf"
        )
        print("✅ Model loaded successfully")

        self.labels = [
            "Payment",
            "Termination",
            "Confidentiality",
            "Liability",
            "Indemnity",
            "Intellectual Property",
            "Governing Law",
            "Warranties",
            "Force Majeure"
        ]

    def predict(self, text: str):
        return self.clf(text, candidate_labels=self.labels)
