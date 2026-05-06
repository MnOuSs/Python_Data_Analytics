# Mental Health Survey Analysis

*This project was developed as part of the IU Internationale Hochschule case study for the course **DLBDSMLUSL01 – Machine Learning: Unsupervised Learning and Feature Engineering**

This project performs data preprocessing, dimensionality reduction using PCA, and clustering analysis (K-Means) on a mental health survey dataset. The goal is to explore patterns, identify clusters, and visualize mental health tendencies based on survey responses.

---

## Features
- Clean and normalize messy survey text data
- Ordinal encoding of qualitative answers
- Handling of missing values
- Standardization of numerical features
- PCA for dimensionality reduction
- K-Means clustering with:
  - Elbow method
  - Silhouette scores
- Clear visualizations of:
  - PCA explained variance
  - Elbow curve
  - Final clusters in PCA space

---

## Project Structure
```
.
├── analysis.py          # Main analysis script
├── preprocessing.py     # Data cleaning and preprocessing pipeline
├── utils.py             # Helper utilities for encoding & cleaning
├── mental-health-in-tech-2016_20161114.csv    # Input dataset
├── figures/               # Generated plots (created at runtime)
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Installation
Clone the repository:
```bash
git clone https://github.com/MnOuSs/mental-health-survey-analysis.git
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage
Run the analysis:
```bash
python analysis.py
```

This will:
- Preprocess the dataset
- Generate PCA
- Compute elbow & silhouette scores
- Create visualizations
- Save output plots inside the `figures/` directory

---

## Dataset Source

This project uses data from the **Mental Health in Tech Survey (2016)** published by OSMI (Open Sourcing Mental Illness).

Dataset link:  
https://www.kaggle.com/datasets/osmi/mental-health-in-tech-2016

Please ensure you comply with the dataset license and usage terms as provided by OSMI and Kaggle.

---
