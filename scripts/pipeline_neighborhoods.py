"""Recurrent neighborhood types analysis - biological novelty."""

import os
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans


def run_neighborhoods(data_dir: str, output_dir: str, k: int = 10, n_clusters: int = 4):
    """Identify recurrent neighborhood types from annotated spatial data."""
    import scanpy as sc

    os.makedirs(output_dir, exist_ok=True)

    # Load annotated data
    ann_path = os.path.join(output_dir, "prostate_annotated.h5ad")
    if not os.path.exists(ann_path):
        raise FileNotFoundError(f"Run annotate first: {ann_path}")

    adata = sc.read_h5ad(ann_path)
    coords = adata.obsm.get("spatial", adata.obsm.get("X_spatial", None))
    if coords is None:
        raise ValueError("No spatial coordinates in AnnData")

    labels = adata.obs["annotation"].astype(str).values
    uniq = np.unique(labels)
    label_to_i = {l: i for i, l in enumerate(uniq)}

    # k-NN neighborhood composition
    nn = NearestNeighbors(n_neighbors=k + 1).fit(coords)
    _, idx = nn.kneighbors(coords)
    idx = idx[:, 1:]  # drop self

    neigh_comp = []
    for row in idx:
        labs = labels[row]
        counts = np.bincount([label_to_i[l] for l in labs], minlength=len(uniq))
        neigh_comp.append(counts / counts.sum())
    neigh_comp = np.vstack(neigh_comp)

    # Cluster neighborhoods
    km = KMeans(n_clusters=n_clusters, random_state=0).fit(neigh_comp)
    adata.obs["neigh_cluster"] = km.labels_.astype(str)

    # Summary
    df = pd.DataFrame(neigh_comp, columns=[f"frac_{u}" for u in uniq])
    df["cluster"] = km.labels_
    summary = df.groupby("cluster").mean()

    out_path = os.path.join(output_dir, "prostate_annotated_neigh.h5ad")
    adata.write_h5ad(out_path)
    summary.to_csv(os.path.join(output_dir, "neighborhood_composition.csv"))

    print(f"Saved: {out_path}")
    print("\nRecurrent neighborhood types")
    print("=" * 50)
    for c in range(n_clusters):
        n = (km.labels_ == c).sum()
        comp = summary.loc[c]
        parts = [f"{u}: {comp[f'frac_{u}']:.2f}" for u in uniq]
        print(f"  Cluster {c} (n={n}): {', '.join(parts)}")
