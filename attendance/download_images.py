# download_images.py
import csv
import os
import re
import requests
import argparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs

def extract_drive_id(url):
    # Try several common Google Drive formats
    if "drive.google.com" not in url:
        return None
    # format: https://drive.google.com/file/d/FILEID/view?usp=sharing
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    # format: https://drive.google.com/open?id=FILEID
    qs = parse_qs(urlparse(url).query)
    if 'id' in qs:
        return qs['id'][0]
    # format: https://drive.google.com/uc?id=FILEID&export=download
    if 'uc' in url:
        m = re.search(r"id=([a-zA-Z0-9_-]+)", url)
        if m:
            return m.group(1)
    return None

def download_file(url, dest_path):
    fid = extract_drive_id(url)
    if fid:
        dl_url = f"https://drive.google.com/uc?export=download&id={fid}"
    else:
        dl_url = url  # fallback: assume direct link

    # Download with streaming
    try:
        r = requests.get(dl_url, stream=True, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    return True

def main(csv_path, link_col, outdir, id_col=None):
    os.makedirs(outdir, exist_ok=True)
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        count = 0
        for row in reader:
            link = row.get(link_col)
            if not link or link.strip()=="":
                continue
            # Determine filename: prefer ID column if provided else use name or index
            base_name = None
            if id_col and row.get(id_col):
                base_name = row[id_col]
            elif row.get("Name"):
                base_name = row["Name"]
            else:
                base_name = f"person_{count+1}"

            # sanitize
            base_name = re.sub(r"[^\w\d_\-]", "_", base_name)

            dest = Path(outdir) / f"{base_name}.jpg"
            print(f"Downloading {link} -> {dest}")
            ok = download_file(link, dest)
            if ok:
                count += 1
            else:
                print(f"Warning: failed to download for row: {row}")
        print(f"Downloaded {count} images into {outdir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--link-col", required=True, help="Column name that contains the image links")
    parser.add_argument("--outdir", default="faces", help="Output folder for images")
    parser.add_argument("--id-col", default=None, help="Optional column to use as filename (StudentID)")
    args = parser.parse_args()
    main(args.csv, args.link_col, args.outdir, args.id_col)
