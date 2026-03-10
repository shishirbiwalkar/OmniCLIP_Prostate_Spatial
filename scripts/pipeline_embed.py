"""Embedding pipeline - generate OmiCLIP embeddings for ST data."""

import os
import numpy as np
import scanpy as sc


def run_embed(data_dir: str, model_dir: str, output_dir: str):
    """Generate transcriptome embeddings for spatial transcriptomics data."""
    os.makedirs(output_dir, exist_ok=True)

    ad_path = os.path.join(data_dir, "prostate.h5ad")
    if not os.path.exists(ad_path):
        print(f"Data not found: {ad_path}. Run: python run.py setup")
        return

    print("Loading data...")
    ad = sc.read_h5ad(ad_path)

    print("Loading OmiCLIP...")
    from scripts.omiclip_model import load_omiclip, encode_text
    from scripts.preprocess import generate_gene_sentences

    model, _, tokenizer = load_omiclip(model_dir, device="cpu")

    print("Generating gene sentences...")
    gene_df = generate_gene_sentences(ad)
    texts = gene_df["label"].tolist()

    print("Encoding transcriptomes...")
    batch_size = 64
    all_emb = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        emb = encode_text(model, tokenizer, batch, "cpu")
        all_emb.append(emb.cpu().numpy())
    embeddings = np.vstack(all_emb)

    ad.obsm["X_omiclip"] = embeddings
    out_path = os.path.join(output_dir, "prostate_embeddings.h5ad")
    ad.write_h5ad(out_path)
    print(f"Saved: {out_path} (shape: {embeddings.shape})")
