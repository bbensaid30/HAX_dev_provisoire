#!/usr/bin/env python3
"""Script de déploiement universel - Phase 3.

Initialise la branche 'main', déploie le pipeline de CI, le README
et le .gitignore sur tous les dépôts étudiants de l'organisation.

Organisation : m1-ssd-2026
Projet : HAX712X (PyArena)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ORG = "m1-ssd-2026"

# Workflow de CI officiel conforme au cahier des charges
WORKFLOW_YAML = """name: CI PyArena - Qualité & Tests

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test-et-qualite:
    runs-on: ubuntu-latest
    steps:
      - name: Récupération du code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Configuration de Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Installation du paquet
        run: |
          pip install -e ".[dev]"

      - name: Contrôle qualité (Ruff)
        run: |
          ruff check src/ tests/
          ruff format --check src/ tests/

      - name: Pytest et Couverture
        run: |
          pytest tests/ --cov=src/pyarena --cov-report=term-missing --cov-report=xml:coverage.xml
"""

GITIGNORE_CONTENT = """# Cache local PokéAPI (Interdit sur GitHub selon cahier des charges)
data/cache/
*.json

# Environnements virtuels
.venv/
venv/
env/

# Fichiers de cache Python et tests
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
coverage.xml

# Distribution & build
build/
dist/
*.egg-info/
"""


def verifier_commandes() -> None:
    for cmd in ("git", "gh"):
        if shutil.which(cmd) is None:
            sys.exit(f"Erreur : la commande '{cmd}' est introuvable.")

    auth = subprocess.run(["gh", "auth", "status"], capture_output=True)
    if auth.returncode != 0:
        sys.exit("Erreur : GitHub CLI n'est pas connecté. Lance 'gh auth login'.")


def recuperer_depots_organisation(org: str) -> list[str]:
    """Récupère la liste exacte des dépôts 'pyarena' existants sur GitHub."""
    cmd = ["gh", "repo", "list", org, "--json", "name", "--limit", "100"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    donnees = json.loads(res.stdout)
    depots = [item["name"] for item in donnees if item["name"].startswith("pyarena")]
    depots.sort()
    return depots


def deployer_vers_depot(tmp_dir: Path, org: str, repo: str) -> bool:
    """Configure le remote et pousse la branche main vers le dépôt cible."""
    url_remote = f"https://github.com/{org}/{repo}.git"

    # Réinitialisation du remote origin
    subprocess.run(["git", "remote", "remove", "origin"], cwd=tmp_dir, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", url_remote], cwd=tmp_dir, check=True)

    # Push forcé pour garantir l'initialisation de la branche main
    res = subprocess.run(
        ["git", "push", "-u", "origin", "main", "--force"],
        cwd=tmp_dir,
        capture_output=True,
        text=True,
    )
    if res.returncode == 0:
        return True

    print(f"\n   [DÉTAIL ERREUR] {res.stderr.strip()}", file=sys.stderr)
    return False


def main() -> None:
    print("=" * 70)
    print(" INITIALISATION ET DÉPLOIEMENT CI VIA GIT")
    print(f" Organisation : {ORG}")
    print("=" * 70)

    verifier_commandes()

    depots = recuperer_depots_organisation(ORG)
    if not depots:
        sys.exit(f"Aucun dépôt préfixé par 'pyarena' trouvé sous {ORG}.")

    print(f"Dépôts détectés ({len(depots)}) : {', '.join(depots)}\n")

    # Création d'un espace de travail temporaire
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)

        # 1. Initialisation d'un dépôt Git local sur la branche 'main'
        subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True)

        # 2. Écriture des fichiers de base
        workflows_dir = tmp_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        (workflows_dir / "ci.yml").write_text(WORKFLOW_YAML, encoding="utf-8")
        (tmp_path / ".gitignore").write_text(GITIGNORE_CONTENT, encoding="utf-8")
        (tmp_path / "README.md").write_text(
            f"# PyArena — HAX712X\nProjet de Développement Logiciel (Promotion M1 SSD 2026)\n",
            encoding="utf-8",
        )

        # 3. Création du commit initial
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "ci: initialisation du dépôt et du workflow de test"],
            cwd=tmp_path,
            check=True,
        )

        # 4. Envoi vers chacun des dépôts étudiants
        succes = 0
        for repo in depots:
            print(f" -> Déploiement sur {ORG}/{repo}...", end=" ", flush=True)
            if deployer_vers_depot(tmp_path, ORG, repo):
                print("[OK]")
                succes += 1
            else:
                print("[ÉCHEC]")

    print("\n" + "=" * 70)
    print(f" Résultat : {succes}/{len(depots)} dépôts configurés et initialisés.")
    print("=" * 70)


if __name__ == "__main__":
    main()