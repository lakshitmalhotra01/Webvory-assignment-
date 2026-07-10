import os
import json
import re

# Raw dataset definitions. We specify the text and the corresponding values for each attribute.
# A script will automatically find the character offsets (start, end) for each entity value.
# This prevents manual alignment errors which cause spaCy's NER parser to crash.

RAW_DATA = [
    # 10 Sample inputs from the assignment description
    {
        "text": "Floor length chiffon bridesmaid dress with pleated bodice and V neckline available in sage and dusty blue",
        "labels": {
            "LENGTH": ["Floor length"],
            "FABRIC": ["chiffon"],
            "CATEGORY": ["bridesmaid dress"],
            "EMBELLISHMENT": ["pleated bodice"],
            "NECKLINE": ["V neckline"],
            "COLOR": ["sage", "dusty blue"]
        }
    },
    {
        "text": "Sparkly sequin fitted prom gown featuring a deep illusion neckline and open back",
        "labels": {
            "EMBELLISHMENT": ["Sparkly", "open back"],
            "FABRIC": ["sequin"],
            "SILHOUETTE": ["fitted"],
            "CATEGORY": ["prom gown"],
            "NECKLINE": ["deep illusion neckline"]
        }
    },
    {
        "text": "Off shoulder satin ball gown with corset bodice and sweep train in royal navy",
        "labels": {
            "NECKLINE": ["Off shoulder"],
            "FABRIC": ["satin"],
            "SILHOUETTE": ["ball gown"],
            "EMBELLISHMENT": ["corset bodice"],
            "LENGTH": ["sweep train"],
            "COLOR": ["royal navy"]
        }
    },
    {
        "text": "Lace mermaid wedding dress with long sleeves and scalloped hem",
        "labels": {
            "FABRIC": ["Lace"],
            "SILHOUETTE": ["mermaid"],
            "CATEGORY": ["wedding dress"],
            "SLEEVE": ["long sleeves"],
            "EMBELLISHMENT": ["scalloped hem"]
        }
    },
    {
        "text": "Short cocktail dress with feather trim and beaded waist detail",
        "labels": {
            "LENGTH": ["Short"],
            "CATEGORY": ["cocktail dress"],
            "EMBELLISHMENT": ["feather trim", "beaded waist detail"]
        }
    },
    {
        "text": "Tulle A line evening gown with floral embroidery and cap sleeves",
        "labels": {
            "FABRIC": ["Tulle"],
            "SILHOUETTE": ["A line"],
            "CATEGORY": ["evening gown"],
            "EMBELLISHMENT": ["floral embroidery"],
            "SLEEVE": ["cap sleeves"]
        }
    },
    {
        "text": "Stretch jersey sheath dress with ruched waist and side slit",
        "labels": {
            "FABRIC": ["Stretch jersey"],
            "SILHOUETTE": ["sheath dress"],
            "EMBELLISHMENT": ["ruched waist", "side slit"]
        }
    },
    {
        "text": "Strapless sweetheart neckline glitter gown with layered skirt",
        "labels": {
            "NECKLINE": ["Strapless", "sweetheart neckline"],
            "FABRIC": ["glitter"],
            "CATEGORY": ["gown"],
            "EMBELLISHMENT": ["layered skirt"]
        }
    },
    {
        "text": "One shoulder draped chiffon dress with high slit and empire waist",
        "labels": {
            "NECKLINE": ["One shoulder"],
            "SILHOUETTE": ["draped"],
            "FABRIC": ["chiffon"],
            "CATEGORY": ["dress"],
            "EMBELLISHMENT": ["high slit", "empire waist"]
        }
    },
    {
        "text": "Velvet winter formal dress with square neckline and puff sleeves",
        "labels": {
            "FABRIC": ["Velvet"],
            "CATEGORY": ["winter formal dress"],
            "NECKLINE": ["square neckline"],
            "SLEEVE": ["puff sleeves"]
        }
    },
    # 50 Additional high-quality descriptions to reach 60 items
    {
        "text": "Elegant knee length crepe shift dress with short sleeves and cowl neck in emerald green",
        "labels": {
            "LENGTH": ["knee length"],
            "FABRIC": ["crepe"],
            "SILHOUETTE": ["shift dress"],
            "SLEEVE": ["short sleeves"],
            "NECKLINE": ["cowl neck"],
            "COLOR": ["emerald green"]
        }
    },
    {
        "text": "Bohemian maxi georgette sun dress with flutter sleeves and ruffled tiers in lavender",
        "labels": {
            "LENGTH": ["maxi"],
            "FABRIC": ["georgette"],
            "CATEGORY": ["sun dress"],
            "SLEEVE": ["flutter sleeves"],
            "EMBELLISHMENT": ["ruffled tiers"],
            "COLOR": ["lavender"]
        }
    },
    {
        "text": "Stunning silk wrap dress with long sleeves and deep V neckline in champagne gold",
        "labels": {
            "FABRIC": ["silk"],
            "SILHOUETTE": ["wrap dress"],
            "SLEEVE": ["long sleeves"],
            "NECKLINE": ["deep V neckline"],
            "COLOR": ["champagne gold"]
        }
    },
    {
        "text": "Sleek column evening gown of heavy satin featuring a high slit and halter neck in burgundy",
        "labels": {
            "SILHOUETTE": ["column"],
            "CATEGORY": ["evening gown"],
            "FABRIC": ["satin"],
            "EMBELLISHMENT": ["high slit"],
            "NECKLINE": ["halter neck"],
            "COLOR": ["burgundy"]
        }
    },
    {
        "text": "Playful mini slip dress with thin spaghetti straps and cowl neck made of glossy silk in blush pink",
        "labels": {
            "LENGTH": ["mini"],
            "SILHOUETTE": ["slip dress"],
            "NECKLINE": ["cowl neck"],
            "FABRIC": ["silk"],
            "COLOR": ["blush pink"]
        }
    },
    {
        "text": "A-line tulle wedding gown with floral lace bodice, long sleeves, and keyhole back in ivory",
        "labels": {
            "SILHOUETTE": ["A-line"],
            "FABRIC": ["tulle", "lace"],
            "CATEGORY": ["wedding gown"],
            "SLEEVE": ["long sleeves"],
            "EMBELLISHMENT": ["keyhole back"],
            "COLOR": ["ivory"]
        }
    },
    {
        "text": "Fitted bodycon midi dress in stretch cotton with scoop neck and short sleeves in charcoal black",
        "labels": {
            "SILHOUETTE": ["Fitted bodycon"],
            "LENGTH": ["midi"],
            "CATEGORY": ["dress"],
            "FABRIC": ["cotton"],
            "NECKLINE": ["scoop neck"],
            "SLEEVE": ["short sleeves"],
            "COLOR": ["charcoal black"]
        }
    },
    {
        "text": "Chic tea length organza party dress with cap sleeves and bow detail in mustard yellow",
        "labels": {
            "LENGTH": ["tea length"],
            "FABRIC": ["organza"],
            "CATEGORY": ["party dress"],
            "SLEEVE": ["cap sleeves"],
            "EMBELLISHMENT": ["bow detail"],
            "COLOR": ["mustard yellow"]
        }
    },
    {
        "text": "Floor length georgette wrap dress with balloon sleeves and tie waist in navy blue",
        "labels": {
            "LENGTH": ["Floor length"],
            "FABRIC": ["georgette"],
            "SILHOUETTE": ["wrap dress"],
            "SLEEVE": ["balloon sleeves"],
            "COLOR": ["navy blue"]
        }
    },
    {
        "text": "Vintage velvet midi dress featuring a square neckline, long sleeves, and side slit in ruby red",
        "labels": {
            "FABRIC": ["velvet"],
            "LENGTH": ["midi"],
            "CATEGORY": ["dress"],
            "NECKLINE": ["square neckline"],
            "SLEEVE": ["long sleeves"],
            "EMBELLISHMENT": ["side slit"],
            "COLOR": ["ruby red"]
        }
    },
    {
        "text": "Glittering sequin ball gown with strapless sweetheart bodice and sweeping court train",
        "labels": {
            "FABRIC": ["sequin"],
            "SILHOUETTE": ["ball gown"],
            "NECKLINE": ["strapless sweetheart"],
            "LENGTH": ["court train"]
        }
    },
    {
        "text": "Linen midi summer dress with side pockets, sleeveless design, and button-down front in white",
        "labels": {
            "FABRIC": ["Linen"],
            "LENGTH": ["midi"],
            "CATEGORY": ["summer dress"],
            "EMBELLISHMENT": ["side pockets"],
            "SLEEVE": ["sleeveless"],
            "COLOR": ["white"]
        }
    },
    {
        "text": "Modern sheath dress in structural crepe with asymmetrical neckline and three-quarter sleeves in plum",
        "labels": {
            "SILHOUETTE": ["sheath dress"],
            "FABRIC": ["crepe"],
            "NECKLINE": ["asymmetrical neckline"],
            "SLEEVE": ["three-quarter sleeves"],
            "COLOR": ["plum"]
        }
    },
    {
        "text": "Boho lace wedding dress with flared bell sleeves, low V back, and floor length skirt",
        "labels": {
            "FABRIC": ["lace"],
            "CATEGORY": ["wedding dress"],
            "SLEEVE": ["bell sleeves"],
            "LENGTH": ["floor length"]
        }
    },
    {
        "text": "Glamorous mermaid prom gown with sequin embroidery, off shoulder neckline, and sweep train in silver",
        "labels": {
            "SILHOUETTE": ["mermaid"],
            "CATEGORY": ["prom gown"],
            "EMBELLISHMENT": ["sequin embroidery"],
            "NECKLINE": ["off shoulder neckline"],
            "LENGTH": ["sweep train"],
            "COLOR": ["silver"]
        }
    },
    {
        "text": "Stretch knit bodycon mini dress featuring a halter neck and cutout details in hot pink",
        "labels": {
            "FABRIC": ["Stretch knit"],
            "SILHOUETTE": ["bodycon"],
            "LENGTH": ["mini"],
            "CATEGORY": ["dress"],
            "NECKLINE": ["halter neck"],
            "EMBELLISHMENT": ["cutout details"],
            "COLOR": ["hot pink"]
        }
    },
    {
        "text": "Sophisticated tweed sheath dress with short sleeves and crewneck neckline in navy blue and white",
        "labels": {
            "FABRIC": ["tweed"],
            "SILHOUETTE": ["sheath dress"],
            "SLEEVE": ["short sleeves"],
            "NECKLINE": ["crewneck neckline"],
            "COLOR": ["navy blue", "white"]
        }
    },
    {
        "text": "Romantic chiffon bridesmaid gown with draped bodice, cap sleeves, and empire waist in sage green",
        "labels": {
            "FABRIC": ["chiffon"],
            "CATEGORY": ["bridesmaid gown"],
            "EMBELLISHMENT": ["draped bodice", "empire waist"],
            "SLEEVE": ["cap sleeves"],
            "COLOR": ["sage green"]
        }
    },
    {
        "text": "Sweetheart neckline satin slip dress with adjustable spaghetti straps in champagne",
        "labels": {
            "NECKLINE": ["Sweetheart neckline"],
            "FABRIC": ["satin"],
            "SILHOUETTE": ["slip dress"],
            "COLOR": ["champagne"]
        }
    },
    {
        "text": "Fitted mermaid wedding dress of delicate corded lace with long sleeves and cathedral train in ivory",
        "labels": {
            "SILHOUETTE": ["Fitted mermaid"],
            "CATEGORY": ["wedding dress"],
            "FABRIC": ["lace"],
            "SLEEVE": ["long sleeves"],
            "LENGTH": ["cathedral train"],
            "COLOR": ["ivory"]
        }
    },
    {
        "text": "Short A-line cocktail dress with organza overlay, puff sleeves, and beaded neckline in rose gold",
        "labels": {
            "LENGTH": ["Short"],
            "SILHOUETTE": ["A-line"],
            "CATEGORY": ["cocktail dress"],
            "FABRIC": ["organza"],
            "SLEEVE": ["puff sleeves"],
            "EMBELLISHMENT": ["beaded neckline"],
            "COLOR": ["rose gold"]
        }
    },
    {
        "text": "Breathable linen wrap dress with flutter sleeves and tie-belt in mustard yellow",
        "labels": {
            "FABRIC": ["linen"],
            "SILHOUETTE": ["wrap dress"],
            "SLEEVE": ["flutter sleeves"],
            "COLOR": ["mustard yellow"]
        }
    },
    {
        "text": "Strapless sweet-heart neckline georgette evening gown with ruched bodice in dusty blue",
        "labels": {
            "NECKLINE": ["Strapless", "sweet-heart neckline"],
            "FABRIC": ["georgette"],
            "CATEGORY": ["evening gown"],
            "EMBELLISHMENT": ["ruched bodice"],
            "COLOR": ["dusty blue"]
        }
    },
    {
        "text": "Structured crepe formal dress with long sleeves and high neck collar in classic black",
        "labels": {
            "FABRIC": ["crepe"],
            "CATEGORY": ["formal dress"],
            "SLEEVE": ["long sleeves"],
            "NECKLINE": ["high neck collar"],
            "COLOR": ["classic black"]
        }
    },
    {
        "text": "Draped silk satin slip dress with cowl neck and side slit in emerald green",
        "labels": {
            "FABRIC": ["silk satin"],
            "SILHOUETTE": ["slip dress"],
            "NECKLINE": ["cowl neck"],
            "EMBELLISHMENT": ["side slit"],
            "COLOR": ["emerald green"]
        }
    },
    {
        "text": "Floor length tulle ball gown with sequin bodice and sleeveless sweetheart neckline in royal blue",
        "labels": {
            "LENGTH": ["Floor length"],
            "FABRIC": ["tulle", "sequin"],
            "SILHOUETTE": ["ball gown"],
            "SLEEVE": ["sleeveless"],
            "NECKLINE": ["sweetheart neckline"],
            "COLOR": ["royal blue"]
        }
    },
    {
        "text": "Casual cotton shirt dress with roll-up sleeves and pocket detail in khaki",
        "labels": {
            "FABRIC": ["cotton"],
            "CATEGORY": ["shirt dress"],
            "SLEEVE": ["roll-up sleeves"],
            "EMBELLISHMENT": ["pocket detail"],
            "COLOR": ["khaki"]
        }
    },
    {
        "text": "Heavy velvet sheath dress featuring a sweetheart neckline, cap sleeves, and ruched waist in deep plum",
        "labels": {
            "FABRIC": ["velvet"],
            "SILHOUETTE": ["sheath dress"],
            "NECKLINE": ["sweetheart neckline"],
            "SLEEVE": ["cap sleeves"],
            "EMBELLISHMENT": ["ruched waist"],
            "COLOR": ["deep plum"]
        }
    },
    {
        "text": "A-line chiffon bridesmaid dress with pleated bodice and cap sleeves in dusty rose",
        "labels": {
            "SILHOUETTE": ["A-line"],
            "FABRIC": ["chiffon"],
            "CATEGORY": ["bridesmaid dress"],
            "EMBELLISHMENT": ["pleated bodice"],
            "SLEEVE": ["cap sleeves"],
            "COLOR": ["dusty rose"]
        }
    },
    {
        "text": "Fitted crepe prom gown with halter neckline and high slit in metallic gold",
        "labels": {
            "SILHOUETTE": ["Fitted"],
            "FABRIC": ["crepe"],
            "CATEGORY": ["prom gown"],
            "NECKLINE": ["halter neckline"],
            "EMBELLISHMENT": ["high slit"],
            "COLOR": ["metallic gold"]
        }
    },
    {
        "text": "Off-shoulder satin ball gown with corset bodice and floor length skirt in royal navy",
        "labels": {
            "NECKLINE": ["Off-shoulder"],
            "FABRIC": ["satin"],
            "SILHOUETTE": ["ball gown"],
            "EMBELLISHMENT": ["corset bodice"],
            "LENGTH": ["floor length"],
            "COLOR": ["royal navy"]
        }
    },
    {
        "text": "Lace mermaid wedding dress with long sleeves and cathedral train in off-white",
        "labels": {
            "FABRIC": ["Lace"],
            "SILHOUETTE": ["mermaid"],
            "CATEGORY": ["wedding dress"],
            "SLEEVE": ["long sleeves"],
            "LENGTH": ["cathedral train"],
            "COLOR": ["off-white"]
        }
    },
    {
        "text": "Short cocktail dress with feather hem and beaded waist detail in midnight black",
        "labels": {
            "LENGTH": ["Short"],
            "CATEGORY": ["cocktail dress"],
            "EMBELLISHMENT": ["feather hem", "beaded waist detail"],
            "COLOR": ["midnight black"]
        }
    },
    {
        "text": "Tulle A-line evening gown with floral embroidery and cap sleeves in dusty blue",
        "labels": {
            "FABRIC": ["Tulle"],
            "SILHOUETTE": ["A-line"],
            "CATEGORY": ["evening gown"],
            "EMBELLISHMENT": ["floral embroidery"],
            "SLEEVE": ["cap sleeves"],
            "COLOR": ["dusty blue"]
        }
    },
    {
        "text": "Stretch jersey sheath dress with ruched waist and side slit in burgundy",
        "labels": {
            "FABRIC": ["Stretch jersey"],
            "SILHOUETTE": ["sheath dress"],
            "EMBELLISHMENT": ["ruched waist", "side slit"],
            "COLOR": ["burgundy"]
        }
    },
    {
        "text": "Strapless sweetheart neckline glitter gown with layered skirt in rose gold",
        "labels": {
            "NECKLINE": ["Strapless", "sweetheart neckline"],
            "FABRIC": ["glitter"],
            "CATEGORY": ["gown"],
            "EMBELLISHMENT": ["layered skirt"],
            "COLOR": ["rose gold"]
        }
    },
    {
        "text": "One-shoulder draped chiffon dress with high slit and empire waist in sage green",
        "labels": {
            "NECKLINE": ["One-shoulder"],
            "SILHOUETTE": ["draped"],
            "FABRIC": ["chiffon"],
            "CATEGORY": ["dress"],
            "EMBELLISHMENT": ["high slit", "empire waist"],
            "COLOR": ["sage green"]
        }
    },
    {
        "text": "Velvet winter formal dress with square neckline and puff sleeves in hunter green",
        "labels": {
            "FABRIC": ["Velvet"],
            "CATEGORY": ["winter formal dress"],
            "NECKLINE": ["square neckline"],
            "SLEEVE": ["puff sleeves"],
            "COLOR": ["hunter green"]
        }
    },
    {
        "text": "Midi satin wrap dress featuring a cowl neckline and long puff sleeves in burgundy red",
        "labels": {
            "LENGTH": ["Midi"],
            "FABRIC": ["satin"],
            "SILHOUETTE": ["wrap dress"],
            "NECKLINE": ["cowl neckline"],
            "SLEEVE": ["long puff sleeves"],
            "COLOR": ["burgundy red"]
        }
    },
    {
        "text": "Beaded lace sheath bridal dress with sweep train and off shoulder sleeves in ivory",
        "labels": {
            "EMBELLISHMENT": ["Beaded"],
            "FABRIC": ["lace"],
            "SILHOUETTE": ["sheath"],
            "CATEGORY": ["bridal dress"],
            "LENGTH": ["sweep train"],
            "NECKLINE": ["off shoulder"],
            "COLOR": ["ivory"]
        }
    },
    {
        "text": "Floor length sequin prom gown with high neckline and long sleeves in champagne silver",
        "labels": {
            "LENGTH": ["Floor length"],
            "FABRIC": ["sequin"],
            "CATEGORY": ["prom gown"],
            "NECKLINE": ["high neckline"],
            "SLEEVE": ["long sleeves"],
            "COLOR": ["champagne silver"]
        }
    },
    {
        "text": "Sweetheart neckline corset ball gown in tiered tulle with cap sleeves in lavender cloud",
        "labels": {
            "NECKLINE": ["Sweetheart neckline"],
            "EMBELLISHMENT": ["corset", "tiered"],
            "SILHOUETTE": ["ball gown"],
            "FABRIC": ["tulle"],
            "SLEEVE": ["cap sleeves"],
            "COLOR": ["lavender cloud"]
        }
    },
    {
        "text": "Sweetheart neck velvet bodycon mini dress with balloon sleeves in wine red",
        "labels": {
            "NECKLINE": ["Sweetheart neck"],
            "FABRIC": ["velvet"],
            "SILHOUETTE": ["bodycon"],
            "LENGTH": ["mini"],
            "CATEGORY": ["dress"],
            "SLEEVE": ["balloon sleeves"],
            "COLOR": ["wine red"]
        }
    },
    {
        "text": "A-line linen summer dress with V-neck design, pockets, and sleeveless styling in ivory white",
        "labels": {
            "SILHOUETTE": ["A-line"],
            "FABRIC": ["linen"],
            "CATEGORY": ["summer dress"],
            "NECKLINE": ["V-neck"],
            "EMBELLISHMENT": ["pockets"],
            "SLEEVE": ["sleeveless"],
            "COLOR": ["ivory white"]
        }
    },
    {
        "text": "Satin mermaid evening gown featuring draped bodice, cowl neck, and thigh high slit in emerald green",
        "labels": {
            "FABRIC": ["Satin"],
            "SILHOUETTE": ["mermaid"],
            "CATEGORY": ["evening gown"],
            "EMBELLISHMENT": ["draped bodice", "thigh high slit"],
            "NECKLINE": ["cowl neck"],
            "COLOR": ["emerald green"]
        }
    },
    {
        "text": "Tiered organza bridesmaid dress with square neckline and short sleeves in blush pink",
        "labels": {
            "EMBELLISHMENT": ["Tiered"],
            "FABRIC": ["organza"],
            "CATEGORY": ["bridesmaid dress"],
            "NECKLINE": ["square neckline"],
            "SLEEVE": ["short sleeves"],
            "COLOR": ["blush pink"]
        }
    },
    {
        "text": "Lace cocktail dress with scoop neckline and three-quarter sleeves in classic black",
        "labels": {
            "FABRIC": ["Lace"],
            "CATEGORY": ["cocktail dress"],
            "NECKLINE": ["scoop neckline"],
            "SLEEVE": ["three-quarter sleeves"],
            "COLOR": ["classic black"]
        }
    },
    {
        "text": "Draped crepe wrap dress with long sleeves and collar neck in mustard yellow",
        "labels": {
            "EMBELLISHMENT": ["Draped"],
            "FABRIC": ["crepe"],
            "SILHOUETTE": ["wrap dress"],
            "SLEEVE": ["long sleeves"],
            "NECKLINE": ["collar neck"],
            "COLOR": ["mustard yellow"]
        }
    },
    {
        "text": "Floor length georgette gown with pleated bodice and cap sleeves in mint green",
        "labels": {
            "LENGTH": ["Floor length"],
            "FABRIC": ["georgette"],
            "CATEGORY": ["gown"],
            "EMBELLISHMENT": ["pleated bodice"],
            "SLEEVE": ["cap sleeves"],
            "COLOR": ["mint green"]
        }
    },
    {
        "text": "Stretch cotton shift dress with short sleeves and crewneck in navy blue",
        "labels": {
            "FABRIC": ["Stretch cotton"],
            "SILHOUETTE": ["shift dress"],
            "SLEEVE": ["short sleeves"],
            "NECKLINE": ["crewneck"],
            "COLOR": ["navy blue"]
        }
    }
]

def find_entity_spans(text, labels_dict):
    """
    Search for labeled entity values inside the text and return a list of spans in the format:
    [start, end, label]
    Ensure spans do not overlap and align perfectly with word boundaries.
    """
    spans = []
    # Sort labels to resolve entities with longer phrases first (helps avoid nested overlaps)
    all_targets = []
    for label, values in labels_dict.items():
        if isinstance(values, str):
            values = [values]
        for val in values:
            all_targets.append((val, label))
    
    # Sort targets by length descending
    all_targets.sort(key=lambda x: len(x[0]), reverse=True)
    
    # Keep track of already matched character positions
    matched_indices = set()
    
    for val, label in all_targets:
        # Search for exact substring matches, case-insensitive, but respecting word boundaries
        # We escape the value to be regex safe
        escaped_val = re.escape(val)
        
        # We search case-insensitively.
        # Find all occurrences
        for match in re.finditer(escaped_val, text, re.IGNORECASE):
            start = match.start()
            end = match.end()
            
            # Check if any character in this span is already matched
            span_indices = set(range(start, end))
            if not span_indices.intersection(matched_indices):
                # Verify that the span matches word boundaries or matches the boundaries of the string
                # We can allow hyphens/spaces as boundaries
                # Let's inspect character before and after
                char_before = text[start - 1] if start > 0 else ' '
                char_after = text[end] if end < len(text) else ' '
                
                # Check word boundaries: non-alphanumeric (except hyphen)
                is_boundary_before = not char_before.isalnum() or char_before == '-'
                is_boundary_after = not char_after.isalnum() or char_after == '-'
                
                if is_boundary_before and is_boundary_after:
                    # Add span
                    spans.append((start, end, label))
                    matched_indices.update(span_indices)
                    break # Only match the first occurrences that don't overlap
    
    # Sort spans by starting index
    spans.sort(key=lambda x: x[0])
    return spans

def main():
    print("Preparing labeled dataset...")
    
    processed_dataset = []
    errors_count = 0
    
    for idx, sample in enumerate(RAW_DATA):
        text = sample["text"]
        labels_dict = sample["labels"]
        
        spans = find_entity_spans(text, labels_dict)
        
        # Verify if all labels were found
        found_values = set()
        for s, e, l in spans:
            found_values.add(text[s:e].lower())
            
        expected_values = []
        for l, vals in labels_dict.items():
            if isinstance(vals, str):
                vals = [vals]
            for v in vals:
                expected_values.append(v.lower())
                
        missing = [v for v in expected_values if v not in found_values]
        if missing:
            print(f"Warning on sample {idx+1}: Could not align offsets for: {missing}")
            print(f"Text: {text}")
            errors_count += 1
            
        # Structure the training data for SpaCy
        # E.g., [text, {"entities": [[start, end, label], ...]}]
        processed_dataset.append({
            "id": idx + 1,
            "text": text,
            "entities": [[s, e, l] for s, e, l in spans]
        })
        
    # Write to data directory
    os.makedirs("data", exist_ok=True)
    dataset_path = "data/labeled_dataset.json"
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(processed_dataset, f, indent=2, ensure_ascii=False)
        
    print(f"Dataset generated successfully at: {dataset_path}")
    print(f"Total samples: {len(processed_dataset)}")
    print(f"Samples with alignment warnings: {errors_count}")

if __name__ == "__main__":
    main()
