import os
import sys
import json
import zipfile
import shutil
import tempfile
import requests

from settings import VERSION, GITHUB_REPO

API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GAME_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_latest_version():
    try:
        resp = requests.get(API_URL, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("tag_name", "")
    except requests.RequestException:
        pass
    return None


def needs_update(latest_version):
    if latest_version is None:
        return False
    return latest_version != VERSION


def download_update(version):
    zip_url = f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{version}.zip"
    try:
        resp = requests.get(zip_url, timeout=30)
        if resp.status_code != 200:
            return None
        temp_dir = tempfile.mkdtemp(prefix="bread_army_update_")
        zip_path = os.path.join(temp_dir, f"{version}.zip")
        with open(zip_path, "wb") as f:
            f.write(resp.content)
        with zipfile.ZipFile(zip_path, "r") as zf:
            top_dir = zf.namelist()[0].split("/")[0]
            zf.extractall(temp_dir)
        return os.path.join(temp_dir, top_dir)
    except (requests.RequestException, zipfile.BadZipFile, OSError):
        return None


def apply_update(update_dir):
    for root, dirs, files in os.walk(update_dir):
        rel_path = os.path.relpath(root, update_dir)
        dest_dir = os.path.join(GAME_DIR, rel_path)
        os.makedirs(dest_dir, exist_ok=True)
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join(dest_dir, f)
            try:
                shutil.copy2(src, dst)
            except PermissionError:
                pass
    return True


def clean_temp(update_dir):
    if update_dir and os.path.exists(os.path.dirname(update_dir)):
        shutil.rmtree(os.path.dirname(update_dir), ignore_errors=True)


def restart():
    python = sys.executable
    os.execl(python, python, *sys.argv)
