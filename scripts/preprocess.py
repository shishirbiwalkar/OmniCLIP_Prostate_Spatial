"""Preprocessing for OmiCLIP - gene sentences from AnnData."""

import pandas as pd


# Housekeeping genes to exclude (subset - full list from MSigDB)
HOUSEKEEPING = {
    "ACTB", "GAPDH", "B2M", "TUBB", "RPLP0", "RPL13A", "PPIA", "PGK1",
    "RPL4", "RPS18", "RPL32", "RPL13", "RPS12", "RPL41", "RPS27A",
}


def generate_gene_sentences(ad, top_k: int = 50):
    """
    Generate top-k gene sentences for each spot (OmiCLIP format).
    Returns DataFrame with 'label' column = space-separated gene symbols.
    """
    import numpy as np

    # Filter genes: exclude those with . or - in name, and housekeeping
    keep = ~ad.var.index.str.contains(r"[.-]", regex=True, na=False)
    keep &= ~ad.var.index.isin(HOUSEKEEPING)
    ad = ad[:, keep].copy()

    if ad.X is None or ad.n_vars == 0:
        raise ValueError("AnnData has no expression matrix or all genes filtered out")

    X = ad.X.toarray() if hasattr(ad.X, "toarray") else np.asarray(ad.X)
    expr = pd.DataFrame(X, index=ad.obs.index, columns=ad.var.index)

    top_genes = expr.apply(lambda s: s.nlargest(min(top_k, len(s))).index.tolist(), axis=1)
    labels = top_genes.apply(lambda x: " ".join(str(g) for g in x))
    return pd.DataFrame({"label": labels})
