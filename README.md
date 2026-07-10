# Product Attribute Extraction Pipeline

A complete, production-grade NLP pipeline that converts unstructured product descriptions into a structured JSON attribute catalog: **Silhouette**, **Fabric**, **Neckline**, **Sleeve**, **Length**, **Embellishment**, **Color**, and **Category**.

This repository implements a full-stack solution featuring:
1. **Data Engineering**: A dataset of 60 product descriptions, programmatically aligned with token-boundary constraints.
2. **Machine Learning**: A custom-trained **SpaCy Named Entity Recognition (NER)** model optimized for high-precision sequence labeling.
3. **Backend API**: A **FastAPI** web server exposing `/extract` endpoints.
4. **Interactive Dashboard**: A **React.js (Vite)** single-page application displaying metrics, live playground text-highlighters, and dataset logs.

---

## 🚀 Quick Start (Single Command)

We provide a master Python orchestrator script (`run.py`) to manage the entire lifecycle of the application.

### Prerequisites
Make sure you have Python 3.8+ and Node.js v18+ installed on your system.

### 1. Run the Entire Build Pipeline
This command programmatically generates the dataset, trains the model, runs evaluation, and compiles the React frontend:
```bash
python run.py all
```
*Note: SpaCy and other Python dependencies must be installed beforehand. If they aren't, run: `pip install spacy fastapi uvicorn pandas scikit-learn pydantic`.*

### 2. Start the Server
Once the build is complete, launch the FastAPI server:
```bash
python run.py serve
```
The server will start at **[http://localhost:8000](http://localhost:8000)**.
- **Frontend Dashboard**: Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Interactive API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

---

## 🛠️ Individual Commands
You can also run individual steps using `run.py`:

- **Data Prep**: `python run.py prepare` -> Compiles `data/labeled_dataset.json`
- **Training**: `python run.py train` -> Trains the NER model and saves weights to `model/best_model/`
- **Evaluation**: `python run.py evaluate` -> Evaluates model on test split and saves `data/evaluation_metrics.json`
- **Frontend Build**: `python run.py build-frontend` -> Compiles React files to `frontend/dist/`
- **API Server**: `python run.py serve` -> Starts the FastAPI backend

---

## 📈 Evaluation Metrics Report
Our model was evaluated on a **20% test split** (12 random samples representing 68 individual entities). The pipeline metrics show exceptionally high performance for domain-specific slot-filling:

- **Overall Span F1-Score**: **90.37%** (Precision: 91.04%, Recall: 89.71%)
- **Overall Slot Accuracy**: **89.58%**

### Attribute-Level Breakdown

| Attribute Label | Span Precision | Span Recall | Span F1-Score | Slot Accuracy | Support |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **SILHOUETTE** | 88.9% | 100.0% | 94.1% | 91.7% | 8 |
| **FABRIC** | 84.6% | 84.6% | 84.6% | 75.0% | 13 |
| **NECKLINE** | 100.0% | 100.0% | 100.0% | 100.0% | 9 |
| **SLEEVE** | 100.0% | 100.0% | 100.0% | 100.0% | 6 |
| **LENGTH** | 100.0% | 66.7% | 80.0% | 91.7% | 3 |
| **EMBELLISHMENT** | 90.9% | 76.9% | 83.3% | 75.0% | 13 |
| **COLOR** | 77.8% | 87.5% | 82.4% | 83.3% | 8 |
| **CATEGORY** | 100.0% | 100.0% | 100.0% | 100.0% | 8 |

---

## 🔍 Common Failure Cases & Mitigation

During rigorous pipeline testing, three primary edge cases were identified as NLP failure modes:

1. **Boundary Ambiguity & Nested Entities**:
   - *Failure Case*: In the description *"Strapless sweetheart neckline glitter gown"*, the parser might struggle to isolate the boundary between `NECKLINE: "Strapless"` and `NECKLINE: "sweetheart neckline"`. It might merge them into a single string.
   - *Mitigation*: We resolve this in data preprocessing by sorting labeled entities by length descending. This trains the model to recognize shorter, distinct sequence tags and prevent boundary nesting.

2. **Modifier Contamination**:
   - *Failure Case*: When colors contain atmospheric words (e.g. *"sage green"* or *"royal navy"* or *"lavender cloud"*), the model sometimes extracts the baseline color (*"sage"*) but misses the modifier (*"green"*), or mislabels *"cloud"* as an embellishment.
   - *Mitigation*: We expand our training corpus to contain multi-word color expressions.

3. **Coordination Conjunctions**:
   - *Failure Case*: In sentences like *"available in sage and dusty blue"*, standard NER pipelines might capture *"sage and dusty blue"* as a single entity or fail to label *"sage"* due to distance from the main modifier.
   - *Mitigation*: We implement post-processing in `api/app.py` that separates coordination groups when generating list fields (like `fabric`, `embellishment`, and `color`).

---

## 🎥 Demo Video Guide
The frontend dashboard is designed to double as an interactive demonstration interface.
To record your demo:
1. Start the server using `python run.py serve` and open [http://localhost:8000](http://localhost:8000).
2. **Playground Tab**: Show the interactive features. Click on one of the sample description chips (e.g., *"Sparkly sequin fitted prom gown..."*). Click **"Extract Attributes"** and show the custom colored entity tokens (displaCy style) and the generated JSON side-by-side.
3. **Performance Tab**: Highlight the metrics table and explain F1-score and Slot-level accuracy.
4. **Dataset Tab**: Type "satin" or "sweetheart" in the search bar to demonstrate dataset query exploration.
5. **Documentation Tab**: Briefly show the methodology report to demonstrate professional project documentation.
