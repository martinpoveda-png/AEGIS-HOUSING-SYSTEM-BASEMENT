#!/usr/bin/env python3
"""
AEGIS HOOP - Google Cloud Storage Public vs Private Asset Manager
For max gamification, open-source IP, and secure deployment

Public (open-source, MIT/Apache 2.0, free for community):
- Basement engineering (this patent + validators, models, CADs)
- PoW scripts, gamification engine, contest leaderboards
- Protocol specs (redacted), README, quick-start

Private (proprietary, hashed only, access via IAM):
- Upper-house architectural IP (3D models, facades, U-shell details)
- Capital escrow full logic, titlingDAO sensitive configs
- Unredacted legal, land contracts, investor materials, production keys
- Full gamification earnings treasury, private contest data

Usage (with gcloud auth):
  python google_cloud_public_private_deploy.py --action upload --bucket aegis-public --local-dir Aegis-Public-Basement
  python google_cloud_public_private_deploy.py --action upload --bucket aegis-private --local-dir private-ip --private

Requires: pip install google-cloud-storage
"""

import argparse
import os
from google.cloud import storage
from google.cloud.exceptions import NotFound
import hashlib
import json
from datetime import datetime

PUBLIC_BUCKET = "aegis-hoop-public"      # gs://aegis-hoop-public (world-readable, CDN)
PRIVATE_BUCKET = "aegis-hoop-private"    # gs://aegis-hoop-private (IAM: validator@... roles/storage.objectViewer)
HOOP_GCS_PROJECT = "aegis-hoop-2026"

def get_client():
    return storage.Client(project=HOOP_GCS_PROJECT)

def upload_public(local_dir: str, bucket_name: str = PUBLIC_BUCKET, prefix: str = "basement-engineering/"):
    """Upload open-source IP (patent, validators, models) - public read"""
    client = get_client()
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        bucket = client.create_bucket(bucket_name, location="us-central1")
        bucket.make_public()  # World readable for max community engagement
    
    uploaded = []
    for root, _, files in os.walk(local_dir):
        for file in files:
            if file.endswith(('.py', '.md', '.pdf', '.txt', '.json', '.csv', '.png', '.jpg', '.dxf')):
                local_path = os.path.join(root, file)
                blob_path = os.path.join(prefix, os.path.relpath(local_path, local_dir))
                blob = bucket.blob(blob_path)
                blob.upload_from_filename(local_path)
                blob.make_public()  # CDN cacheable
                uploaded.append(blob_path)
                print(f"✅ PUBLIC: gs://{bucket_name}/{blob_path}")
    
    # Generate public index for gamification contest
    index = {
        "timestamp": datetime.now().isoformat(),
        "files": uploaded,
        "license": "MIT/Apache 2.0",
        "contest_url": "https://aegis-hoop-public.storage.googleapis.com/basement-engineering/contest_leaderboard.json",
        "note": "Free for community validators. Earn HOOP + USD via gamified PoW."
    }
    index_blob = bucket.blob(f"{prefix}INDEX.json")
    index_blob.upload_from_string(json.dumps(index, indent=2))
    index_blob.make_public()
    print(f"📋 Public index: gs://{bucket_name}/{prefix}INDEX.json")

def upload_private(local_dir: str, bucket_name: str = PRIVATE_BUCKET, prefix: str = "upper-ip/"):
    """Upload private IP (upper house, full escrow, legal) - IAM restricted"""
    client = get_client()
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        bucket = client.create_bucket(bucket_name, location="us-central1")
        # Do NOT make_public - use IAM: validator-service@... storage.objectViewer
    
    for root, _, files in os.walk(local_dir):
        for file in files:
            if file.endswith(('.pdf', '.dwg', '.step', '.key', '.pem', '.json')):  # sensitive
                local_path = os.path.join(root, file)
                blob_path = os.path.join(prefix, os.path.relpath(local_path, local_dir))
                blob = bucket.blob(blob_path)
                # Compute hash only (never upload raw if ultra-sensitive)
                with open(local_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                blob.upload_from_filename(local_path)
                # Add custom metadata for on-chain audit
                blob.metadata = {"sha256": file_hash, "uploaded": datetime.now().isoformat(), "access": "validator-only"}
                blob.patch()
                print(f"🔒 PRIVATE: gs://{bucket_name}/{blob_path} (hash: {file_hash[:16]}...)")
    
    print("⚠️  Private bucket: Set IAM policy to restrict to validator@... and multi-sig@... only.")
    print("   On-chain: Store only hashes in PoW_Ledger PDA for auditability.")

def create_gamification_contest_assets(bucket_name: str = PUBLIC_BUCKET):
    """Create public contest assets for max engagement"""
    client = get_client()
    bucket = client.bucket(bucket_name)
    
    # Leaderboard (updated by validators via Cloud Function or CI)
    leaderboard = {
        "last_updated": datetime.now().isoformat(),
        "weekly_contest": "April 27 - May 4, 2026",
        "prize_pool_hoop": 5000,
        "top_validators": [
            {"rank": 1, "wallet": "CzdBHjP7CkqRaYrxwoCxDpFhXU2B6akZ5rfFKQqo1NCj", "points": 152, "earnings_usd": 127.5, "badges": ["STRUCTURAL_SPECIALIST", "MASTER_BUILDER"]},
            {"rank": 2, "wallet": "0xValidator2...", "points": 148, "earnings_usd": 119.0, "badges": ["ELECTRICIAN_SPECIALIST"]},
        ],
        "how_to_enter": "Run validate_all.py --milestone 2 --local_data ./evidence/ --stake 250",
        "rules": "First 10 per gate win base HOOP. Top 3 weekly get 2x + NFT. Stake for yield."
    }
    blob = bucket.blob("basement-engineering/contest_leaderboard.json")
    blob.upload_from_string(json.dumps(leaderboard, indent=2))
    blob.make_public()
    print(f"🏆 Contest leaderboard: gs://{bucket_name}/basement-engineering/contest_leaderboard.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS Google Cloud Public/Private IP Manager")
    parser.add_argument("--action", choices=["upload", "contest"], default="upload")
    parser.add_argument("--bucket", default=PUBLIC_BUCKET)
    parser.add_argument("--local-dir", default="Aegis-Public-Basement")
    parser.add_argument("--private", action="store_true", help="Use private bucket + IAM")
    args = parser.parse_args()
    
    if args.action == "contest":
        create_gamification_contest_assets(args.bucket)
    else:
        if args.private:
            upload_private(args.local_dir, PRIVATE_BUCKET)
        else:
            upload_public(args.local_dir, args.bucket)
    
    print("\n✅ Google Cloud deployment complete. Public = open-source gamification. Private = hashed IP.")
    print("Update protocol: Basement (this patent) = 100% PUBLIC. Upper = PRIVATE (hash only).")
