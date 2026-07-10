import os
import json
import spacy

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_slots(text, spans):
    """
    Convert a list of spans [start, end, label] to a dictionary of slots.
    For each slot, value is a list of strings sorted and lowercased.
    """
    slots = {
        "SILHOUETTE": [],
        "FABRIC": [],
        "NECKLINE": [],
        "SLEEVE": [],
        "LENGTH": [],
        "EMBELLISHMENT": [],
        "COLOR": [],
        "CATEGORY": []
    }
    for start, end, label in spans:
        val = text[start:end].strip()
        if label in slots:
            slots[label].append(val.lower())
            
    # Sort lists to ensure list comparisons don't fail on ordering
    for label in slots:
        slots[label].sort()
        
    return slots

def main():
    print("Evaluating trained model on test split...")
    
    model_dir = "model/best_model"
    test_split_path = "data/test_split.json"
    
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Trained model not found at {model_dir}. Train the model first.")
    if not os.path.exists(test_split_path):
        raise FileNotFoundError(f"Test split not found at {test_split_path}. Train the model first.")
        
    nlp = spacy.load(model_dir)
    test_data = load_json(test_split_path)
    
    # Track statistics for span-level evaluation (NER metrics)
    span_stats = {} # {LABEL: {tp, fp, fn}}
    labels = ["SILHOUETTE", "FABRIC", "NECKLINE", "SLEEVE", "LENGTH", "EMBELLISHMENT", "COLOR", "CATEGORY"]
    for l in labels:
        span_stats[l] = {"tp": 0, "fp": 0, "fn": 0}
        
    # Track statistics for slot-level accuracy
    slot_correct_counts = {l: 0 for l in labels}
    total_samples = len(test_data)
    
    for sample in test_data:
        text = sample["text"]
        gold_spans = sample["entities"]
        
        # 1. Predict entities
        doc = nlp(text)
        pred_spans = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        
        # 2. Evaluate spans (NER metrics)
        gold_tuples = set((s, e, l) for s, e, l in gold_spans)
        pred_tuples = set(pred_spans)
        
        # Compute true positives, false positives, false negatives for spans
        for s, e, l in gold_tuples:
            if (s, e, l) in pred_tuples:
                if l in span_stats:
                    span_stats[l]["tp"] += 1
            else:
                if l in span_stats:
                    span_stats[l]["fn"] += 1
                    
        for s, e, l in pred_tuples:
            if (s, e, l) not in gold_tuples:
                if l in span_stats:
                    span_stats[l]["fp"] += 1
                    
        # 3. Evaluate slots (structured attributes accuracy)
        gold_slots = extract_slots(text, gold_spans)
        pred_slots = extract_slots(text, pred_spans)
        
        for slot in labels:
            if gold_slots[slot] == pred_slots[slot]:
                slot_correct_counts[slot] += 1
                
    # 4. Compile metrics
    span_metrics = {}
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    for l in labels:
        tp = span_stats[l]["tp"]
        fp = span_stats[l]["fp"]
        fn = span_stats[l]["fn"]
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0
        
        # Slot accuracy
        accuracy = slot_correct_counts[l] / total_samples
        
        span_metrics[l] = {
            "span_precision": round(p, 4),
            "span_recall": round(r, 4),
            "span_f1": round(f1, 4),
            "slot_accuracy": round(accuracy, 4),
            "support": tp + fn
        }
        
    # Micro-average overall
    overall_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    overall_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = 2 * (overall_p * overall_r) / (overall_p + overall_r) if (overall_p + overall_r) > 0 else 0.0
    overall_slot_accuracy = sum(slot_correct_counts.values()) / (total_samples * len(labels))
    
    summary = {
        "attribute_metrics": span_metrics,
        "overall": {
            "precision": round(overall_p, 4),
            "recall": round(overall_r, 4),
            "f1_score": round(overall_f1, 4),
            "slot_accuracy": round(overall_slot_accuracy, 4),
            "total_test_samples": total_samples
        }
    }
    
    # Save evaluation report
    report_path = "data/evaluation_metrics.json"
    save_json(summary, report_path)
    
    # Print metrics report
    print("\n================ EVALUATION METRICS REPORT ================")
    print(f"Total Test Samples: {total_samples}")
    print(f"Overall Span Precision: {summary['overall']['precision']:.4f}")
    print(f"Overall Span Recall:    {summary['overall']['recall']:.4f}")
    print(f"Overall Span F1-Score:  {summary['overall']['f1_score']:.4f}")
    print(f"Overall Slot Accuracy:  {summary['overall']['slot_accuracy']:.4f}")
    print("-----------------------------------------------------------")
    print(f"{'Attribute':<16} | {'Precision':<9} | {'Recall':<9} | {'F1-Score':<9} | {'Slot Acc':<9} | {'Support':<7}")
    print("-----------------------------------------------------------")
    for l in labels:
        m = span_metrics[l]
        print(f"{l:<16} | {m['span_precision']:<9.4f} | {m['span_recall']:<9.4f} | {m['span_f1']:<9.4f} | {m['slot_accuracy']:<9.4f} | {m['support']:<7}")
    print("===========================================================\n")
    print(f"Detailed metrics saved to: {report_path}")

if __name__ == "__main__":
    main()
