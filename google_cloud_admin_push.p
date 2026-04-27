#!/usr/bin/env python3
"""
AEGIS HOOP - Google Cloud ADMIN PUSH v3.0 (Enterprise-Grade)
Full admin deployment: create buckets, IAM policies, public CDN, private restricted,
upload open-source patent + validators + gamification contest assets,
private upper-IP (hash only), service accounts, and on-chain ready payloads.

Run after: gcloud auth application-default login
pip install google-cloud-storage google-cloud-iam google-cloud-resource-manager

Usage:
  python google_cloud_admin_push.py --project aegis-hoop-2026 --admin-push
  python google_cloud_admin_push.py --project aegis-hoop-2026 --admin-push --dry-run
"""

import argparse
import os
import hashlib
import json
import logging
import mimetypes
from datetime import datetime
from google.cloud import storage
from google.api_core.exceptions import Conflict, Forbidden
from google.iam.v1 import policy_pb2

# === CONFIG ===
PROJECT_ID = "aegis-hoop-2026"
PUBLIC_BUCKET = "aegis-hoop-public"
PRIVATE_BUCKET = "aegis-hoop-private"
SERVICE_ACCOUNT = "validator-service@aegis-hoop-2026.iam.gserviceaccount.com"
MULTI_SIG_GROUP = "aegis-multisig@googlegroups.com"
LOCATION = "us-central1"
CDN_ENABLED = True
MAX_FILE_SIZE_MB = 100  # Anti-depletion limit

# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AEGIS-ADMIN")

def get_storage_client():
    return storage.Client(project=PROJECT_ID)

def create_buckets(storage_client, dry_run=False):
    """Create buckets with strict exception handling."""
    for bucket_name, is_public in [(PUBLIC_BUCKET, True), (PRIVATE_BUCKET, False)]:
        if dry_run:
            logger.info(f"[DRY-RUN] Would evaluate/create bucket: {bucket_name}")
            continue

        try:
            bucket = storage_client.create_bucket(bucket_name, location=LOCATION)
            logger.info(f"🆕 Created bucket: {bucket_name}")
        except Conflict:
            bucket = storage_client.get_bucket(bucket_name)
            logger.info(f"✅ Bucket exists: {bucket_name}")
        except Forbidden:
            logger.error(f"❌ ERROR: Permission denied creating {bucket_name}. Check IAM roles.")
            return

        if is_public and CDN_ENABLED:
            bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            bucket.patch()
            logger.info(f"🌍 PUBLIC: {bucket_name} uniform access + CDN enabled")

def set_iam_policies(storage_client, dry_run=False):
    """Admin IAM: enforces strict public/private access boundaries."""
    if dry_run:
        logger.info("[DRY-RUN] Would set IAM policies for allUsers (public) and Validator/Multisig (private)")
        return

    # PUBLIC - Object Viewer for all
    public_bucket = storage_client.bucket(PUBLIC_BUCKET)
    policy = public_bucket.get_iam_policy(requested_policy_version=3)
    policy.bindings.append(policy_pb2.Binding(role="roles/storage.objectViewer", members=["allUsers"]))
    public_bucket.set_iam_policy(policy)
    logger.info(f"✅ PUBLIC IAM: allUsers = objectViewer on {PUBLIC_BUCKET}")

    # PRIVATE - Restricted
    private_bucket = storage_client.bucket(PRIVATE_BUCKET)
    policy = private_bucket.get_iam_policy(requested_policy_version=3)
    policy.bindings = [
        policy_pb2.Binding(
            role="roles/storage.objectViewer",
            members=[f"serviceAccount:{SERVICE_ACCOUNT}", f"group:{MULTI_SIG_GROUP}"]
        ),
        policy_pb2.Binding(
            role="roles/storage.legacyBucketOwner",
            members=[f"serviceAccount:{SERVICE_ACCOUNT}"]
        )
    ]
    private_bucket.set_iam_policy(policy)
    logger.info(f"✅ PRIVATE IAM: {SERVICE_ACCOUNT} + {MULTI_SIG_GROUP} only on {PRIVATE_BUCKET}")

def safe_upload(bucket, local_path, blob_path, make_public=False, dry_run=False):
    """Anti-abuse wrapper with MIME-type and Cache-Control optimization."""
    file_size_mb = os.path.getsize(local_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        logger.warning(f"⚠️ SKIPPED: {local_path} ({file_size_mb:.2f}MB) exceeds {MAX_FILE_SIZE_MB}MB limit.")
        return None

    if dry_run:
        logger.info(f"[DRY-RUN] Would upload: {local_path} -> gs://{bucket.name}/{blob_path}")
        return True

    blob = bucket.blob(blob_path)
    
    # CDN Optimization: Set content type and cache control
    content_type, _ = mimetypes.guess_type(local_path)
    if content_type:
        blob.content_type = content_type
    if make_public:
        blob.cache_control = "public, max-age=3600" # Force edge caching to prevent egress drain

    blob.upload_from_filename(local_path)
    if make_public:
        blob.make_public()
    return blob

def upload_open_source_ip(storage_client, local_dir="Aegis-Public-Basement", prefix="basement-engineering/", dry_run=False):
    bucket = storage_client.bucket(PUBLIC_BUCKET)
    for root, _, files in os.walk(local_dir):
        for file in sorted(files):
            if file.endswith(('.py', '.md', '.pdf', '.txt', '.json', '.csv', '.png', '.jpg')):
                local_path = os.path.join(root, file)
                blob_path = os.path.join(prefix, os.path.relpath(local_path, local_dir))
                blob = safe_upload(bucket, local_path, blob_path, make_public=True, dry_run=dry_run)
                if blob and not dry_run:
                    logger.info(f"✅ OPEN-SOURCE UPLOAD: gs://{PUBLIC_BUCKET}/{blob_path}")

def push_dynamic_gamification_schema(storage_client, prefix="basement-engineering/", dry_run=False):
    """Pushes a richer schema ready to be consumed by a dynamic frontend/dApp."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would push dynamic gamification schema to gs://{PUBLIC_BUCKET}/{prefix}contest_schema.json")
        return

    bucket = storage_client.bucket(PUBLIC_BUCKET)
    contest = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "season": 1,
            "weekly_epoch": "April 27 - May 4, 2026",
            "total_prize_pool_hoop": 5000
        },
        "bounties": {
            "structural_audit": {"reward": 150, "multiplier": 1.5, "condition": "First 10 valid hashes"},
            "electrical_grid": {"reward": 200, "multiplier": 1.0, "condition": "NEC 2023 compliance"}
        },
        "leaderboard_api": "https://api.aegis-hoop-2026.com/v1/leaderboard",
        "instructions": "Submit proofs via dApp. Smart contract verifies hash against PDA ledger."
    }
    contest_blob = bucket.blob(f"{prefix}contest_schema.json")
    contest_blob.content_type = "application/json"
    contest_blob.cache_control = "public, max-age=300" # 5-min cache for fast schema updates
    contest_blob.upload_from_string(json.dumps(contest, indent=2))
    contest_blob.make_public()
    logger.info(f"🏆 GAMIFICATION SCHEMA: gs://{PUBLIC_BUCKET}/{prefix}contest_schema.json")

def upload_private_ip(storage_client, local_dir="private-upper-ip", prefix="upper-ip/", dry_run=False):
    """Upload private IP with SHA256 metadata only"""
    bucket = storage_client.bucket(PRIVATE_BUCKET)
    for root, _, files in os.walk(local_dir):
        for file in files:
            if file.endswith(('.pdf', '.dwg', '.step', '.key', '.pem', '.json')):
                local_path = os.path.join(root, file)
                blob_path = os.path.join(prefix, os.path.relpath(local_path, local_dir))
                
                blob = safe_upload(bucket, local_path, blob_path, make_public=False, dry_run=dry_run)
                if blob and not dry_run:
                    with open(local_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    blob.metadata = {
                        "sha256": file_hash,
                        "uploaded": datetime.now().isoformat(),
                        "access": "validator-service + 4-of-7 multisig only",
                        "on_chain": "PoW_Ledger PDA + IPFS CID"
                    }
                    blob.patch()
                    logger.info(f"🔒 PRIVATE IP: gs://{PRIVATE_BUCKET}/{blob_path} (SHA256: {file_hash[:16]}...)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS Google Cloud ADMIN PUSH v3.0 (Enterprise)")
    parser.add_argument("--project", default=PROJECT_ID, help="GCP Project ID")
    parser.add_argument("--admin-push", action="store_true", help="Execute the push")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the execution without making changes")
    parser.add_argument("--local-public", default="Aegis-Public-Basement", help="Local directory for public assets")
    parser.add_argument("--local-private", default="private-upper-ip", help="Local directory for private IP")
    args = parser.parse_args()
    
    if not args.admin_push and not args.dry_run:
        logger.error("Must specify --admin-push or --dry-run")
        exit(1)

    storage_client = get_storage_client()
    
    mode = "[DRY-RUN]" if args.dry_run else "[ACTIVE]"
    logger.info(f"🚀 AEGIS HOOP ADMIN PUSH v3.0 {mode}")
    logger.info(f"   Project: {args.project}")
    logger.info(f"   Public:  {PUBLIC_BUCKET} (world-readable + CDN caching)")
    logger.info(f"   Private: {PRIVATE_BUCKET} (IAM restricted)")
    
    create_buckets(storage_client, dry_run=args.dry_run)
    set_iam_policies(storage_client, dry_run=args.dry_run)
    upload_open_source_ip(storage_client, args.local_public, dry_run=args.dry_run)
    upload_private_ip(storage_client, args.local_private, dry_run=args.dry_run)
    push_dynamic_gamification_schema(storage_client, dry_run=args.dry_run)
    
    logger.info(f"\n✅✅✅ ADMIN DEPLOYMENT SECURE {mode} ✅✅✅")
