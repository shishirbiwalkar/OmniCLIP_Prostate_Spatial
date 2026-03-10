#OmniCLIP

**Simple bioinformatics pipelines** for histopathology + spatial transcriptomics using the [OmiCLIP/Loki](https://www.nature.com/articles/s41592-025-02707-1) foundation model (Nature Methods 2025).

##Biological novelty

**Recurrent neighborhood types**: We identify spatially recurrent microenvironment patterns by clustering local neighborhood composition (k-NN). Each spot's neighborhood is summarized as the fraction of tumor/stroma/normal among its k nearest neighbors; K-means clustering yields recurrent types (e.g. stroma-dominant, normal-dominant, mixed). This addresses the question: *Are there recurrent neighborhood types?* — yes, 4 distinct types in our analysis.

##Quick Start (1–2 commands)

```bash
# 1. Install & setup (first time only)
pip install -r requirements.txt
python run.py setup

# 2. Run pipelines
python run.py annotate       # Tissue annotation (tumor/stroma/normal)
python run.py embed         # Generate OmiCLIP embeddings
python run.py neighborhoods # Recurrent neighborhood types (biological novelty)

# Or: ./run.sh setup && ./run.sh annotate && python run.py neighborhoods
```

##What It Does

| Command | Description |
|---------|-------------|
| `python run.py setup` | Downloads OmiCLIP model + spatial transcriptomics sample |
| `python run.py annotate` | Annotates tissue using marker genes (tumor, stroma, normal) |
| `python run.py embed` | Generates 768-d embeddings for downstream analysis |
| `python run.py neighborhoods` | Identifies recurrent neighborhood types (biological novelty) |

##Dataset

- **Primary**: [10x Visium FFPE Human Prostate Cancer](https://www.10xgenomics.com/datasets) via squidpy
- **Fallback**: [V1 Human Lymph Node](https://support.10xgenomics.com/spatial-gene-expression/datasets) (scanpy) — 500 spots, 36,601 genes
- **Model**: OmiCLIP pretrained weights from [Hugging Face](https://huggingface.co/WangGuangyuLab/Loki)

##Output

- `output/prostate_annotated.h5ad` – AnnData with `annotation` and `tumor_score`
- `output/prostate_embeddings.h5ad` – AnnData with `X_omiclip` embeddings
- `output/prostate_annotated_neigh.h5ad` – AnnData with `neigh_cluster` (recurrent neighborhood types)
- `output/neighborhood_composition.csv` – Mean composition per neighborhood cluster
- `output/annotation_plot.png` – Spatial scatter of annotations

##Reference

Chen, W. et al. A visual–omics foundation model to bridge histopathology with spatial transcriptomics. *Nature Methods* **22**, 1568–1582 (2025). [DOI](https://doi.org/10.1038/s41592-025-02707-1)
# OmniCLIP_Prostate_Spatial
