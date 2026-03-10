#!/usr/bin/env python3
"""
OmniCLIP - One-command bioinformatics pipelines for histopathology + spatial transcriptomics.
Based on OmiCLIP/Loki (Nature Methods 2025): https://www.nature.com/articles/s41592-025-02707-1

Usage (1-2 lines):
  python run.py annotate          # Tissue annotation with marker genes
  python run.py embed             # Generate image + transcriptome embeddings
  python run.py setup             # Download model + prostate sample data
"""

import argparse
import os
import sys

# Add parent for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def cmd_setup(args):
    """Download OmiCLIP model and prostate sample data."""
    from scripts.setup_data import run_setup
    run_setup(args.data_dir, args.model_dir)


def cmd_annotate(args):
    """Annotate tissue patches using marker genes (tumor vs normal)."""
    from scripts.pipeline_annotate import run_annotate
    run_annotate(
        data_dir=args.data_dir,
        model_dir=args.model_dir,
        output_dir=args.output_dir,
    )


def cmd_embed(args):
    """Generate OmiCLIP embeddings for ST data and H&E images."""
    from scripts.pipeline_embed import run_embed
    run_embed(
        data_dir=args.data_dir,
        model_dir=args.model_dir,
        output_dir=args.output_dir,
    )


def cmd_neighborhoods(args):
    """Identify recurrent neighborhood types (biological novelty)."""
    from scripts.pipeline_neighborhoods import run_neighborhoods
    run_neighborhoods(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
    )


def main():
    parser = argparse.ArgumentParser(
        description="OmniCLIP - Simple pipelines for histopathology + transcriptomics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py setup              # First time: download model + data
  python run.py annotate           # Annotate tissue (tumor/stroma/normal)
  python run.py embed             # Generate embeddings
  python run.py neighborhoods     # Recurrent neighborhood types (biological novelty)
        """,
    )
    parser.add_argument(
        "--data-dir", default="data",
        help="Data directory (default: data)",
    )
    parser.add_argument(
        "--model-dir", default="models",
        help="Model weights directory (default: models)",
    )
    parser.add_argument(
        "--output-dir", default="output",
        help="Output directory (default: output)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    p_setup = subparsers.add_parser("setup", help="Download model + prostate sample data")
    p_setup.set_defaults(func=cmd_setup)

    # annotate
    p_annotate = subparsers.add_parser("annotate", help="Tissue annotation with marker genes")
    p_annotate.set_defaults(func=cmd_annotate)

    # embed
    p_embed = subparsers.add_parser("embed", help="Generate OmiCLIP embeddings")
    p_embed.set_defaults(func=cmd_embed)

    # neighborhoods
    p_neigh = subparsers.add_parser("neighborhoods", help="Recurrent neighborhood types")
    p_neigh.set_defaults(func=cmd_neighborhoods)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
