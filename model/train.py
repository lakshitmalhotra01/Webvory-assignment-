import os
import json
import random
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

def load_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def evaluate_model(nlp, test_data):
    """
    Compute micro-averaged Precision, Recall, and F1 score on a test set.
    """
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    for sample in test_data:
        text = sample["text"]
        gold_entities = sample["entities"] # List of [start, end, label]
        
        doc = nlp(text)
        pred_entities = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        
        # Convert list of lists to list of tuples for hashing
        gold_tuples = set((start, end, label) for start, end, label in gold_entities)
        pred_tuples = set(pred_entities)
        
        tp = len(gold_tuples.intersection(pred_tuples))
        fp = len(pred_tuples - gold_tuples)
        fn = len(gold_tuples - pred_tuples)
        
        true_positives += tp
        false_positives += fp
        false_negatives += fn
        
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1

def main():
    print("Initializing SpaCy NER training pipeline...")
    
    # 1. Load and split dataset
    dataset_path = "data/labeled_dataset.json"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Labeled dataset not found. Run prepare_dataset.py first.")
        
    dataset = load_data(dataset_path)
    
    # Shuffle and split (80% train, 20% test)
    # Fixed seed for reproducibility
    random.seed(42)
    random.shuffle(dataset)
    
    split_idx = int(len(dataset) * 0.8)
    train_data = dataset[:split_idx]
    test_data = dataset[split_idx:]
    
    print(f"Splitting dataset: {len(train_data)} train samples, {len(test_data)} test samples.")
    
    # Save the splits so evaluation runs on the exact same test split
    save_data(train_data, "data/train_split.json")
    save_data(test_data, "data/test_split.json")
    
    # 2. Create blank English model and add NER
    nlp = spacy.blank("en")
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
        
    # Add labels to NER
    labels = set()
    for sample in dataset:
        for ent in sample["entities"]:
            labels.add(ent[2])
            
    print(f"Entities to extract: {sorted(list(labels))}")
    for label in labels:
        ner.add_label(label)
        
    # 3. Initialize model
    optimizer = nlp.initialize()
    
    # 4. Training loop
    epochs = 80
    best_f1 = -1.0
    best_model_dir = "model/best_model"
    
    print(f"Starting training loop ({epochs} epochs)...")
    for epoch in range(epochs):
        random.shuffle(train_data)
        losses = {}
        
        # Batching using SpaCy compounding batch size
        batches = minibatch(train_data, size=compounding(4.0, 16.0, 1.001))
        for batch in batches:
            examples = []
            for sample in batch:
                text = sample["text"]
                entities = sample["entities"]
                
                doc = nlp.make_doc(text)
                # Formulate entities as a dictionary of spans
                gold_dict = {"entities": [(s, e, l) for s, e, l in entities]}
                examples.append(Example.from_dict(doc, gold_dict))
                
            nlp.update(examples, sgd=optimizer, drop=0.2, losses=losses)
            
        # Evaluate at the end of every 5th epoch and the final epoch
        p, r, f1 = evaluate_model(nlp, test_data)
        
        if (epoch + 1) % 5 == 0 or epoch == 0 or epoch == epochs - 1:
            print(f"Epoch {epoch+1:02d} | Loss: {losses['ner']:.4f} | Test Precision: {p:.4f} | Test Recall: {r:.4f} | Test F1: {f1:.4f}")
            
        # Save the best model
        if f1 >= best_f1:
            best_f1 = f1
            os.makedirs(best_model_dir, exist_ok=True)
            nlp.to_disk(best_model_dir)
            
    print(f"Training completed. Best Test F1: {best_f1:.4f}")
    print(f"Best model saved to: {best_model_dir}")

if __name__ == "__main__":
    main()
