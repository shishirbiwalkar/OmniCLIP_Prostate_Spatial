"""Download OmiCLIP model and prostate sample data."""

import os


def run_setup(data_dir: str, model_dir: str):
    """Download pretrained OmiCLIP weights and prostate Visium sample."""
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    print("OmniCLIP Setup")
    print("=" * 50)

    # 1. Download OmiCLIP model from Hugging Face
    model_path = os.path.join(model_dir, "checkpoint.pt")
    if not os.path.exists(model_path):
        print("Downloading OmiCLIP pretrained weights...")
        url = "https://huggingface.co/WangGuangyuLab/Loki/resolve/main/checkpoint.pt"
        try:
            from huggingface_hub import hf_hub_download
            path = hf_hub_download(
                repo_id="WangGuangyuLab/Loki",
                filename="checkpoint.pt",
                local_dir=model_dir,
            )
            if path != model_path and os.path.exists(path):
                import shutil
                shutil.move(path, model_path)
            print(f"  Saved to {model_path}")
        except Exception as e:
            print(f"  HuggingFace failed: {e}")
            try:
                import urllib.request
                urllib.request.urlretrieve(url, model_path)
                print(f"  Saved via direct download to {model_path}")
            except Exception as e2:
                print(f"  Direct download failed: {e2}")
                print("  Manual: download from https://huggingface.co/WangGuangyuLab/Loki")
    else:
        print(f"Model already exists: {model_path}")

    # 2. Download prostate sample via squidpy
    prostate_path = os.path.join(data_dir, "prostate.h5ad")
    if not os.path.exists(prostate_path):
        print("Downloading prostate cancer Visium sample (squidpy)...")
        try:
            import squidpy as sq
            adata = sq.datasets.visium("Visium_FFPE_Human_Prostate_Cancer")
            # Subset for speed (first 500 spots)
            n = min(500, adata.n_obs)
            adata = adata[:n].copy()
            adata.write_h5ad(prostate_path)
            print(f"  Saved to {prostate_path} ({adata.n_obs} spots, {adata.n_vars} genes)")
        except Exception as e:
            print(f"  Squidpy download failed: {e}")
            # Fallback: visium_hne_adata (mouse, but works for demo)
            try:
                adata = sq.datasets.visium_hne_adata()
                adata = adata[:500].copy()
                adata.write_h5ad(prostate_path)
                print(f"  Fallback: saved visium_hne to {prostate_path}")
            except Exception as e2:
                print(f"  Fallback failed: {e2}")
                print("  Create data/prostate.h5ad manually from 10x Visium data.")
                return
    else:
        print(f"Prostate data already exists: {prostate_path}")

    print("=" * 50)
    print("Setup complete. Run: python run.py annotate")
