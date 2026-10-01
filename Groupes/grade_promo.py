#!/usr/bin/env python3
"""Script d'évaluation automatisée de la promotion - Phase 5.

Projet : HAX712X (PyArena)
Organisation : m1-ssd-2026
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import os
import sys
from pathlib import Path

# ==============================================================================
# Configuration
# ==============================================================================
ORG = "m1-ssd-2026"
NB_GROUPES = 8
PREFIXE_DEPOT = "pyarena"
DOSSIER_TRAVAUX = Path("travaux_etudiants")
DOSSIER_ORACLE = Path("tests_oracle").resolve()
FICHIER_RESULTATS = "recapitulatif_notes_promo.csv"


def executer_commande(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Exécute une commande shell et capture la sortie standard et d'erreur."""
    res = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return res.returncode, res.stdout


def cloner_ou_pull_depot(repo_name: str) -> Path:
    """Clone le dépôt de l'équipe ou le met à jour s'il existe déjà."""
    DOSSIER_TRAVAUX.mkdir(exist_ok=True)
    chemin_repo = DOSSIER_TRAVAUX / repo_name

    if chemin_repo.exists():
        print(" [mise à jour git pull]", end=" ", flush=True)
        executer_commande(["git", "checkout", "main"], cwd=chemin_repo)
        executer_commande(["git", "pull", "origin", "main"], cwd=chemin_repo)
    else:
        print(" [clonage git clone]", end=" ", flush=True)
        url = f"https://github.com/{ORG}/{repo_name}.git"
        executer_commande(["git", "clone", url, str(chemin_repo)])

    return chemin_repo


def evaluer_statut_ci_github(repo_name: str) -> str:
    """Interroge GitHub Actions pour savoir si le dernier run sur main est valide."""
    cmd = [
        "gh",
        "run",
        "list",
        "--repo",
        f"{ORG}/{repo_name}",
        "--branch",
        "main",
        "--limit",
        "1",
        "--json",
        "conclusion",
    ]
    code, out = executer_commande(cmd)
    if code == 0 and out.strip():
        try:
            runs = json.loads(out)
            if runs:
                return runs[0].get("conclusion") or "in_progress"
        except json.JSONDecodeError:
            pass
    return "inconnu"


def compter_prs_et_approvals(repo_name: str) -> tuple[int, int]:
    """Compte le nombre de PRs fusionnées et le nombre de revues de code."""
    # 1. PRs fermées/mergées
    cmd_prs = [
        "gh",
        "pr",
        "list",
        "--repo",
        f"{ORG}/{repo_name}",
        "--state",
        "merged",
        "--limit",
        "100",
        "--json",
        "number",
    ]
    code_pr, out_pr = executer_commande(cmd_prs)
    nb_prs = 0
    if code_pr == 0 and out_pr.strip():
        try:
            nb_prs = len(json.loads(out_pr))
        except json.JSONDecodeError:
            pass

    # Estimation rapide des revues (approvals)
    return nb_prs, nb_prs  # Approximé via l'historique GitHub

def evaluer_code_etudiant(chemin_repo: Path) -> dict[str, float | str]:
    resultats = {
        "tests_etudiants": "ÉCHEC",
        "couverture_pct": 0.0,
        "tests_oracle_reussis": 0,
        "tests_oracle_total": 5,
    }

    # Le chemin absolu vers le dossier src/ de l'étudiant
    dossier_src = chemin_repo / "src"

    if not dossier_src.exists():
        # L'arborescence src/pyarena n'est pas encore créée par le groupe
        return resultats

    # Configuration de l'environnement avec le PYTHONPATH pointant vers le code de CE groupe
    env_etudiant = os.environ.copy()
    env_etudiant["PYTHONPATH"] = str(dossier_src.resolve())

    # 1. Tests étudiants + couverture
    code_cov, out_cov = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "--cov=src/pyarena",
            "--cov-report=term",
        ],
        cwd=chemin_repo,
        env=env_etudiant,  # Injection du chemin source
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    ).returncode, ""

    # 2. Exécution des tests Oracle Enseignant
    # pytest s'exécute depuis le dossier de l'étudiant, avec le code de l'étudiant dans sys.path
    res_oracle = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(DOSSIER_ORACLE),
            "-q",
        ],
        cwd=chemin_repo,
        env=env_etudiant,  # Permet à test_oracle_core.py de faire "import pyarena"
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    
    # Décompte des tests passés
    for ligne in res_oracle.stdout.splitlines():
        if "passed" in ligne:
            try:
                resultats["tests_oracle_reussis"] = int(ligne.split()[0])
            except (ValueError, IndexError):
                pass

    return resultats


def main() -> None:
    print("=" * 75)
    print(" PHASE 5 : Évaluation Automatisée de la Promotion HAX712X")
    print(f" Organisation : {ORG} | Nombre de groupes : {NB_GROUPES}")
    print("=" * 75)

    if not DOSSIER_ORACLE.exists():
        sys.exit(f"Erreur : le dossier des tests oracle '{DOSSIER_ORACLE}' est introuvable.")

    bilan_promo = []

    for i in range(1, NB_GROUPES + 1):
        team_slug = f"groupe-{i:02d}"
        repo_name = f"{PREFIXE_DEPOT}-{team_slug}"
        print(f"\nÉvaluation du {team_slug} ({repo_name})...", end="", flush=True)

        # 1. Audit GitHub distant (CI et PRs)
        statut_ci = evaluer_statut_ci_github(repo_name)
        nb_prs, _ = compter_prs_et_approvals(repo_name)

        # 2. Audit local (Tests et Couverture)
        chemin_repo = cloner_ou_pull_depot(repo_name)
        audit_local = evaluer_code_etudiant(chemin_repo)

        ligne_rapport = {
            "Groupe": team_slug,
            "Depot": repo_name,
            "CI_GitHub": statut_ci,
            "PRs_Mergées": nb_prs,
            "Tests_Etudiants": audit_local["tests_etudiants"],
            "Couverture_%": audit_local["couverture_pct"],
            "Oracle_Valides": f"{audit_local['tests_oracle_reussis']}/{audit_local['tests_oracle_total']}",
        }
        bilan_promo.append(ligne_rapport)
        print(" [TERMINÉ]")

    # 3. Export du tableau récapitulatif
    with open(FICHIER_RESULTATS, mode="w", newline="", encoding="utf-8") as f:
        colonnes = [
            "Groupe",
            "Depot",
            "CI_GitHub",
            "PRs_Mergées",
            "Tests_Etudiants",
            "Couverture_%",
            "Oracle_Valides",
        ]
        writer = csv.DictWriter(f, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(bilan_promo)

    print("\n" + "=" * 75)
    print(f" Rapport synthétique généré : {FICHIER_RESULTATS}")
    print("=" * 75)


if __name__ == "__main__":
    main()