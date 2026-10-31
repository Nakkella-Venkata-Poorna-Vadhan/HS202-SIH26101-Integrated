import hashlib
import os
import subprocess

def get_file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_git_blob_sha256(repo, commit_ref, rel_path):
    cmd = ["git", "-C", repo, "show", f"{commit_ref}:{rel_path}"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        return None, res.stderr.decode("utf-8", errors="ignore").strip()
    return hashlib.sha256(res.stdout).hexdigest(), None

orig_repo = r"D:\Projects\SIH26101\SIH26101-Integrated"
phase1_repo = r"D:\Projects\SIH26101\SIH26101-Integrated-Phase1"

# All files touched or mentioned during earlier sessions/operations
files_to_check = [
    "frontend/src/context/AppContext.tsx",
    "backend/data/learners/learning_activities.json",
    "frontend/src/services/api.ts",
    "frontend/src/types/index.ts",
    "frontend/src/App.tsx",
    "frontend/src/pages/LoginPage.tsx",
    "backend/competency_engine/api.py",
    "backend/competency_engine/db/models.py",
    "backend/competency_engine/db/__init__.py",
    "backend/scripts/init_docker_postgres.sh",
    "backend/scripts/init_docker_postgres.sql",
    "docker-compose.yml",
    "README.md",
]

print(f"=== Comprehensive SHA-256 Integrity Report ===")
print(f"Original Repository: {orig_repo}")
print(f"Phase 1 Reference:   {phase1_repo} (commit c05e663)\n")

for rel_path in files_to_check:
    full_path = os.path.join(orig_repo, rel_path.replace("/", os.sep))
    if not os.path.exists(full_path):
        print(f"[-] {rel_path}: NOT FOUND ON DISK")
        continue

    disk_sha = get_file_sha256(full_path)
    git_head_sha, head_err = get_git_blob_sha256(orig_repo, "HEAD", rel_path)
    p1_sha, p1_err = get_git_blob_sha256(phase1_repo, "c05e663", rel_path)

    matches_git_head = (disk_sha == git_head_sha)
    matches_phase1 = (disk_sha == p1_sha) if p1_sha else False

    status_str = "MATCHES HEAD" if matches_git_head else "MODIFIED FROM HEAD"
    print(f"File: {rel_path}")
    print(f"  Disk Working Tree SHA-256: {disk_sha}")
    print(f"  Git HEAD Object SHA-256:   {git_head_sha} [{status_str}]")
    if p1_sha:
        print(f"  Phase 1 Baseline SHA-256:  {p1_sha} [{'MATCHES PHASE 1' if matches_phase1 else 'DIFFERS FROM PHASE 1'}]")
    else:
        print(f"  Phase 1 Baseline SHA-256:  N/A ({p1_err})")
    print()

