"""
Analysis script for mental health survey clustering.

This module loads and preprocesses survey data, performs PCA for dimensionality
reduction, evaluates clustering performance using the elbow and silhouette
methods, and visualizes final K-Means clusters.
"""

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from preprocessing import preprocess


# Load and preprocess dataset
df = preprocess("mental-health-in-tech-2016_20161114.csv")
X = df.values

# STANDARDIZE
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA: Dimensionality Reduction
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

plt.figure()
plt.plot(
    range(1, len(pca.explained_variance_ratio_) + 1),
    pca.explained_variance_ratio_,
    marker='o'
)
plt.title("Explained Variance Ratio per PCA Component")
plt.xlabel("Component")
plt.ylabel("Variance Ratio")
plt.savefig("figures/pca_explained_variance.png", dpi=300)

# Elbow Method to Determine Optimal k
inertia_list = []
K = range(2, 10)

for k in K:
    km = KMeans(n_clusters=k, random_state=42)
    km.fit(X_pca[:, :2])  # use first two principal components
    inertia_list.append(km.inertia_)

plt.figure()
plt.plot(K, inertia_list, marker='o')
plt.title("Elbow Method")
plt.xlabel("k")
plt.ylabel("Inertia")
plt.savefig("figures/elbow_method.png", dpi=300)

# Silhouette Scores for Each k
for k in range(2, 10):
    km = KMeans(n_clusters=k, random_state=42)
    labels = km.fit_predict(X_pca[:, :2])
    score = silhouette_score(X_pca[:, :2], labels)
    print(k, score)

# Final Clustering and Visualization
km = KMeans(n_clusters=3, random_state=42)
labels = km.fit_predict(X_pca[:, :2])

plt.figure()
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap="viridis")
plt.title("K-Means Clusters on PCA Components")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.savefig("figures/k-means_clusters.png", dpi=300)
