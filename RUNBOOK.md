# Operations Runbook

## 1. Dependency Pinning Strategy

We ensure reproducibility by pinning all Python dependencies to exact versions in `app/requirements.txt`:

```
flask==3.0.0
scikit-learn==1.3.2
gunicorn==21.2.0
```

**How it works:**
- All packages use `==` to lock to specific versions (no `>=` or `~=`)
- `requirements.txt` is the single source of truth for runtime dependencies
- The Docker builder stage installs from this file with `pip install --no-cache-dir`
- To update dependencies: bump versions, test locally, then update the lock file

**Verification:**
```bash
pip freeze | grep -E "flask|scikit-learn|gunicorn"
```

---

## 2. Image Optimization

### Before vs After Optimization

| Stage | Size | Technique |
|-------|------|-----------|
| Base python:3.11 | ~130 MB | - |
| + Full dependencies (single-stage) | ~450 MB | Dev tools, build artifacts |
| **Optimized multi-stage** | **~280 MB** | Builder/runtime separation |

### Techniques Used

1. **Multi-stage build:** Dependencies installed in builder stage; only `/root/.local` (installed packages) copied to runtime. Build tools and intermediate layers are discarded.

2. **Layer ordering:** `COPY app/requirements.txt` before `COPY app/` so dependency layer is cached when only code changes.

3. **Minimal base:** `python:3.11-slim` instead of `python:3.11` (saves ~800MB).

4. **.dockerignore:** Excludes tests, venv, IDE config, PDFs, and other non-runtime files from the build context.

5. **Non-root user:** Reduces attack surface; app runs as `appuser` instead of root.

**Check image size:**
```bash
docker build -t ml-service:test .
docker images ml-service:test --format "{{.Size}}"
```

---

## 3. Security Considerations

- **Minimal attack surface:** Runtime image contains only Flask, scikit-learn, and gunicorn. No compilers, shells (beyond minimal), or dev tools.

- **Non-root execution:** Container runs as unprivileged `appuser`; no root inside the container.

- **No hardcoded credentials:** Registry auth uses GitHub Secrets (`GITHUB_TOKEN`); no secrets in code or config.

- **Pinned dependencies:** Avoids supply-chain surprises; versions are auditable.

- **Vulnerability scanning:** Use Trivy (optional) to scan images:
  ```bash
  trivy image ghcr.io/bsing30/milestone2:v1.0.0
  ```

---

## 4. CI/CD Workflow (Step-by-Step)

The `.github/workflows/build.yml` pipeline runs on push to `main`/`master` and on version tags (`v*`).

### Step 1: Test Job
- Checkout code
- Set up Python 3.11
- Install `app/requirements.txt` and pytest
- Run `pytest tests/ -v`
- **Exit condition:** Test job must succeed before build runs

### Step 2: Build Job (runs only if test passes)
- Depends on `test` via `needs: test`
- Checkout code
- Set up Docker Buildx
- **Authenticate** to GitHub Container Registry using `GITHUB_TOKEN` (from `secrets.GITHUB_TOKEN`)
- **Extract version:**
  - On tag push (e.g. `v1.0.0`): use that tag
  - On branch push: use `v0.0.0-<short-sha>`
- **Build and push** image to `ghcr.io/<owner>/milestone2:<version>`

### Flow Diagram
```
Push/PR → Checkout → Test (pytest) → [PASS] → Build → Login → Push
                        ↓
                    [FAIL] → Pipeline fails, no push
```

---

## 5. Versioning Strategy (Semantic Versioning)

We use [Semantic Versioning](https://semver.org/) (vX.Y.Z):

- **X (major):** Breaking API or model changes
- **Y (minor):** New features, backward compatible
- **Z (patch):** Bug fixes, no behavior change

**Tagging examples:**
```bash
# First release
git tag v1.0.0
git push origin v1.0.0

# Patch fix
git tag v1.0.1
git push origin v1.0.1
```

Images are tagged as `ghcr.io/bsing30/milestone2:v1.0.0`. Branch pushes use `v0.0.0-<sha>` for dev builds.

---

## 6. Troubleshooting

### Image push fails with authentication error
- **Cause:** Registry credentials missing or incorrect.
- **Solution:** Ensure GitHub Actions has `packages: write` permission. For GHCR, `GITHUB_TOKEN` is provided automatically. For other registries, add `REGISTRY_USERNAME` and `REGISTRY_PASSWORD` as repository secrets.

### Tests pass locally but fail in CI
- **Cause:** Environment differences (paths, Python version, missing files).
- **Solution:** Run tests in a clean environment: `docker run --rm -v $(pwd):/app -w /app python:3.11-slim pytest tests/ -v`. Ensure `model.pkl` exists before running tests (run `python train_model.py` first).

### Image size too large (>500MB)
- **Cause:** Extra layers, full base image, or large artifacts.
- **Solution:** Use `python:3.11-slim`, multi-stage build, and `.dockerignore`. Verify with `docker history <image>`.

### Build takes too long
- **Cause:** Poor layer caching or large context.
- **Solution:** `.dockerignore` excludes unnecessary files. Dependencies are cached; only app code changes invalidate later layers. Use Buildx cache (already configured in workflow).

### Container exits immediately
- **Cause:** Missing `model.pkl`, wrong CMD, or port binding.
- **Solution:** Run `python train_model.py` before `docker build`. Ensure `app/model.pkl` is committed or built into the image. Check logs: `docker run --rm <image>`.

### Port 8080 already in use
- **Cause:** Another process using port 8080.
- **Solution:** Use a different host port: `docker run -p 9090:8080 <image>`.
