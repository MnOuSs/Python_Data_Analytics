"""
Data preprocessing utilities for cleaning survey data, encoding qualitative
responses, handling missing values, and preparing a structured dataset for
analysis.

"""

import pandas as pd
from utils import clean_text, encode_ordinal

# List of relevant survey questions to keep during preprocessing
FEATURES = [
    "Do you feel that being identified as a person with a mental health issue would hurt your career?",
    "Have you heard of or observed negative consequences for co-workers who have been open about mental health issues in your workplace?",
    "Would you feel comfortable discussing a mental health disorder with your direct supervisor(s)?",
    "Do you feel that your employer takes mental health as seriously as physical health?",
    "Does your employer offer resources to learn more about mental health concerns and options for seeking help?",
    "Is your anonymity protected if you choose to take advantage of mental health or substance abuse treatment resources provided by your employer?",
    "What is your age?",
    "What is your gender?"
]

def load_and_select(path):
    """
    Load a CSV file and select only the features of interest.

    """
    df = pd.read_csv(path, engine="python", on_bad_lines="skip")
    return df[FEATURES]

def clean_and_encode(df):
    """
    Clean text fields and encode ordinal and categorical variables.

    Cleaning steps include:
    - Lowercasing and trimming text
    - Removing punctuation
    - Encoding ordinal responses using `encode_ordinal`
    - Encoding gender as categorical codes

    """
    # Apply text normalization to all columns
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    # Encode the first six features using the ordinal mapping
    ordinal_cols = FEATURES[:6]
    for col in ordinal_cols:
        df[col] = df[col].apply(encode_ordinal)

    # Encode gender as category codes
    df["What is your gender?"] = df["What is your gender?"].astype("category").cat.codes

    return df

def handle_missing(df):
    """
    Handle missing values by dropping rows missing age and filling other
    missing values with the mode of each column.

    """
    # Drop records missing required age information
    df = df.dropna(subset=["What is your age?"])

    # Fill remaining missing values with column mode
    for col in df.columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    return df

def preprocess(path):
    """
    Full preprocessing pipeline: load data, clean/encode it, and handle
    missing values.

    """
    df = load_and_select(path)
    df = clean_and_encode(df)
    df = handle_missing(df)
    return df
