"""Tissue annotation pipeline - marker gene based (Loki Annotate style)."""

import os
import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib.pyplot as plt


# Prostate marker genes (from literature / Nature paper)
MARKERS = {
    "tumor": "TP53 EPCAM KRAS EGFR KRT18 KRT8 KRT19 CDH17 CK20 DSP NKX3-1 AMACR",
    "stroma": "COL1A1 COL1A2 COL3A1 FN1 DCN LUM ACTA2 PDGFRA",
    "normal": "NKX3-1 KLK3 ACPP MSMB NDRG1",
}


def run_annotate(data_dir: str, model_dir: str, output_dir: str):
    """Annotate tissue patches using marker genes."""
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    ad_path = os.path.join(data_dir, "prostate.h5ad")
    if not os.path.exists(ad_path):
        print(f"Data not found: {ad_path}")
        print("Run first: python run.py setup")
        return

    print("Loading prostate data...")
    ad = sc.read_h5ad(ad_path)

    # Check for H&E image in adata
    has_image = "spatial" in ad.uns and len(ad.uns["spatial"]) > 0
    lib_id = list(ad.uns["spatial"].keys())[0] if has_image else None

    # Load model
    print("Loading OmiCLIP model...")
    from scripts.omiclip_model import load_omiclip, encode_text, encode_images
    from scripts.preprocess import generate_gene_sentences

    model, preprocess, tokenizer = load_omiclip(model_dir, device="cpu")

    # Encode marker gene sentences
    print("Encoding marker genes...")
    marker_texts = list(MARKERS.values())
    marker_emb = encode_text(model, tokenizer, marker_texts, "cpu")
    marker_names = list(MARKERS.keys())

    # Encode transcriptomes (gene sentences from ST data)
    print("Encoding transcriptomes...")
    gene_df = generate_gene_sentences(ad)
    texts = gene_df["label"].tolist()
    # Batch encode (chunks to avoid OOM)
    batch_size = 64
    all_emb = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        emb = encode_text(model, tokenizer, batch, "cpu")
        all_emb.append(emb)
    st_emb = np.vstack([e.cpu().numpy() for e in all_emb])

    # Similarity: each spot vs each tissue type
    sim = st_emb @ marker_emb.cpu().numpy().T
    pred = np.argmax(sim, axis=1)
    ad.obs["annotation"] = [marker_names[i] for i in pred]
    tidx = marker_names.index("tumor") if "tumor" in marker_names else 0
    ad.obs["tumor_score"] = sim[:, tidx]

    # Save
    out_path = os.path.join(output_dir, "prostate_annotated.h5ad")
    ad.write_h5ad(out_path)
    print(f"Saved: {out_path}")

    # Summary
    print("\nAnnotation summary:")
    print(ad.obs["annotation"].value_counts())

    # Plot if spatial coords exist
    if "spatial" in ad.obsm or "X_spatial" in ad.obsm:
        coords = ad.obsm.get("spatial", ad.obsm.get("X_spatial", None))
        if coords is not None:
            fig, ax = plt.subplots(1, 1, figsize=(6, 5))
            for label in ad.obs["annotation"].unique():
                mask = ad.obs["annotation"] == label
                ax.scatter(coords[mask, 0], coords[mask, 1], label=label, s=8, alpha=0.7)
            ax.legend()
            ax.set_title("OmiCLIP tissue annotation (marker genes)")
            ax.set_xlabel("x"); ax.set_ylabel("y")
            plt.tight_layout()
            plot_path = os.path.join(output_dir, "annotation_plot.png")
            plt.savefig(plot_path, dpi=150)
            plt.close()
            print(f"Plot saved: {plot_path}")
