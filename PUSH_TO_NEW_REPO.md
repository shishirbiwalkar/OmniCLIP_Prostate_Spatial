#Push OmniCLIP to a new GitHub repository

##Step 1: Create the repo on GitHub

1. Go to https://github.com/new
2. Repository name: **OmniCLIP**
3. Description: Simple pipelines for histopathology + spatial transcriptomics (OmiCLIP). Biological novelty: recurrent neighborhood types.
4. Choose **Public**
5. Do **not** initialize with README (we already have one)
6. Click **Create repository**

##Step 2: Push from terminal

```bash
cd /Users/shishirbiwalkar/genomic-ai-project/OmniCLIP-standalone
git remote add origin https://github.com/shishirbiwalkar/OmniCLIP.git
git push -u origin main
```

(If you already added the remote, just run `git push -u origin main`)

##Using SSH instead

```bash
git remote set-url origin git@github.com:shishirbiwalkar/OmniCLIP.git
git push -u origin main
```
