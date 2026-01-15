from transformers import pipeline
from typing import List, Dict, Union

class ZeroShotClassifier:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-mnli",
        labels: List[str] = None,
        device: int = -1  # -1 for CPU, 0 for first GPU
    ):
        print("⏳ Loading Zero-Shot model... (first run may take time)")
        self.clf = pipeline(
            "zero-shot-classification",
            model=model_name,
            framework="pt",  # use 'pt' for PyTorch, better support for GPU
            device=device
        )
        print("✅ Model loaded successfully")

        # Default labels if none provided
        self.labels = labels or [
            "Period",
            "Notice Period",
            "Payment",
            "Termination",
            "Confidentiality",
            "Liability",
            "Indemnity",
            "Intellectual Property",
            "Governing Law",
            "Warranties",
            "Force Majeure",
            "Maintenance",
            "Use of Premises",
            "Alteration",
            "Inspection",
            "Registration"
        ]

    def predict(self, texts: Union[str, List[str]], top_k: int = 3, threshold: float = 0.0) -> List[Dict]:
        """
        Predict labels for a single text or a list of texts.
        Returns top_k labels with optional threshold filtering.
        """
        if isinstance(texts, str):
            texts = [texts]

        results = []
        for text in texts:
            output = self.clf(text, candidate_labels=self.labels)
            # Filter by threshold
            filtered = [
                {"label": lbl, "score": score}
                for lbl, score in zip(output["labels"], output["scores"])
                if score >= threshold
            ][:top_k]

            results.append({
                "text": text,
                "top_label": filtered[0]["label"] if filtered else None,
                "predictions": filtered
            })
        return results

