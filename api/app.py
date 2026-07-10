import os
import json
import spacy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

app = FastAPI(
    title="Product Attribute Extraction API",
    description="FastAPI service to extract structured fashion attributes from unstructured product descriptions.",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained SpaCy model
MODEL_PATH = "model/best_model"
nlp = None
if os.path.exists(MODEL_PATH):
    try:
        nlp = spacy.load(MODEL_PATH)
        print(f"Loaded SpaCy model from: {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model from {MODEL_PATH}: {e}")
else:
    print(f"Warning: Model path {MODEL_PATH} not found. Please train the model first.")

# Request schema
class ExtractRequest(BaseModel):
    text: str

# Helper to format SpaCy entities into structured attributes
def format_attributes(text, doc):
    attributes = {
        "silhouette": None,
        "fabric": [],
        "neckline": None,
        "sleeve": None,
        "length": None,
        "embellishment": [],
        "color": [],
        "category": None
    }
    
    for ent in doc.ents:
        label = ent.label_.lower()
        val = ent.text.strip()
        
        if label == "silhouette":
            attributes["silhouette"] = val
        elif label == "fabric":
            if val not in attributes["fabric"]:
                attributes["fabric"].append(val)
        elif label == "neckline":
            attributes["neckline"] = val
        elif label == "sleeve":
            attributes["sleeve"] = val
        elif label == "length":
            attributes["length"] = val
        elif label == "embellishment":
            if val not in attributes["embellishment"]:
                attributes["embellishment"].append(val)
        elif label == "color":
            if val not in attributes["color"]:
                attributes["color"].append(val)
        elif label == "category":
            attributes["category"] = val
            
    return attributes

# Helper to clean up empty list values if they should be null,
# but for fashion metadata, returning empty lists for multi-value attributes is standard.
# Let's keep them as lists for fabric, color, embellishment, and strings/nulls for others.

@app.post("/extract")
def extract_attributes(request: ExtractRequest):
    """
    Standard endpoint as requested in the assignment details.
    Input: {"text": "..."}
    Output: Flat structured JSON attributes
    """
    if nlp is None:
        raise HTTPException(status_code=503, detail="Model is not loaded. Train the model first.")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
    doc = nlp(request.text)
    attributes = format_attributes(request.text, doc)
    return attributes

@app.post("/api/extract")
def extract_attributes_detailed(request: ExtractRequest):
    """
    Detailed extraction endpoint for the frontend dashboard.
    Returns attributes plus raw entity spans for visual text highlighting.
    """
    if nlp is None:
        raise HTTPException(status_code=503, detail="Model is not loaded. Train the model first.")
        
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
    doc = nlp(request.text)
    attributes = format_attributes(request.text, doc)
    
    # Extract spans for visual highlighter
    entities = []
    for ent in doc.ents:
        entities.append({
            "start": ent.start_char,
            "end": ent.end_char,
            "label": ent.label_,
            "text": ent.text
        })
        
    return {
        "text": request.text,
        "attributes": attributes,
        "entities": entities
    }

@app.get("/api/metrics")
def get_metrics():
    """
    Return the model evaluation metrics.
    """
    metrics_path = "data/evaluation_metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise HTTPException(status_code=404, detail="Metrics not found. Run model/evaluate.py first.")

@app.get("/api/dataset")
def get_dataset():
    """
    Return the labeled dataset.
    """
    dataset_path = "data/labeled_dataset.json"
    if os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise HTTPException(status_code=404, detail="Dataset not found. Run data/prepare_dataset.py first.")

# Serve compiled React App
DIST_PATH = "frontend/dist"
if os.path.exists(DIST_PATH):
    # Serve index.html at root
    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(DIST_PATH, "index.html"))
        
    # Serve assets and static files
    app.mount("/", StaticFiles(directory=DIST_PATH, html=True), name="static")
    
    # Catch-all routing for React router (SPA)
    @app.exception_handler(404)
    def catch_all_404(request, exc):
        return FileResponse(os.path.join(DIST_PATH, "index.html"))
else:
    @app.get("/")
    def serve_fallback():
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>Product Attribute Extraction Service</title>
                    <style>
                        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
                        h1 { color: #38bdf8; margin-bottom: 10px; }
                        p { color: #94a3b8; font-size: 1.1rem; }
                        .btn { background: #0284c7; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 20px; transition: background 0.2s; }
                        .btn:hover { background: #0369a1; }
                    </style>
                </head>
                <body>
                    <h1>Product Attribute Extraction API</h1>
                    <p>The backend API is running successfully.</p>
                    <p style="color: #f43f5e; font-size: 0.9rem;">(React Frontend has not been built yet. Run 'python run.py build-frontend' to compile and serve the dashboard here.)</p>
                    <a href="/docs" class="btn">View Swagger API Docs</a>
                </body>
            </html>
            """,
            status_code=200
        )
