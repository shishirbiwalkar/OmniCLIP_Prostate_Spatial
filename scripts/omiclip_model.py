"""OmiCLIP model loader - uses open_clip like Loki."""

import os
import torch
import torch.nn.functional as F
from PIL import Image


def load_omiclip(model_path: str, device: str = "cpu"):
    """
    Load OmiCLIP model from checkpoint.
    Uses create_model_from_pretrained (Loki) or create_model_and_transforms (fallback).
    """
    from open_clip import get_tokenizer

    ckpt = os.path.join(model_path, "checkpoint.pt") if os.path.isdir(model_path) else model_path
    if not os.path.exists(ckpt):
        raise FileNotFoundError(f"Model not found: {ckpt}. Run: python run.py setup")

    # PyTorch 2.6+ uses weights_only=True by default; Loki checkpoint needs weights_only=False
    try:
        from open_clip import create_model_and_transforms
        model, _, preprocess = create_model_and_transforms("coca_ViT-L-14", pretrained=None)
        state = torch.load(ckpt, map_location=device, weights_only=False)
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        model.load_state_dict(state, strict=False)
        model = model.to(device)
    except Exception:
        from open_clip import create_model_from_pretrained
        model, preprocess = create_model_from_pretrained(
            "coca_ViT-L-14", device=device, pretrained=ckpt
        )

    tokenizer = get_tokenizer("coca_ViT-L-14")
    model.eval()
    return model, preprocess, tokenizer


def encode_text(model, tokenizer, texts, device="cpu"):
    """Encode text/gene sentences to embeddings."""
    text_inputs = tokenizer(texts)
    with torch.no_grad():
        feats = model.encode_text(text_inputs).to(device)
    return F.normalize(feats, p=2, dim=-1)


def encode_images(model, preprocess, image_paths, device="cpu"):
    """Encode images to embeddings."""
    embeddings = []
    for p in image_paths:
        img = Image.open(p).convert("RGB")
        x = torch.stack([preprocess(img)]).to(device)
        with torch.no_grad():
            feats = model.encode_image(x)
        embeddings.append(feats)
    out = torch.cat(embeddings, dim=0)
    return F.normalize(out, p=2, dim=-1)
