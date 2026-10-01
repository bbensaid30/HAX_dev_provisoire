#!/usr/bin/env python3
"""Script d'orchestration - Phase 2 : Création des dépôts et affectation des droits.

Projet : HAX712X (PyArena)
Organisation : univ-montpellier-hax712x-2026
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

# ==============================================================================
# Configuration
# ==============================================================================
ORG = "m1-ssd-2026"
NB_GROUPES = 8
PREFIXE_DEPOT = "pyarena"

# Si True, GitHub crée un premier commit avec un README.md vierge (crée la branche 'main').
# Si False, le dépôt est strictement vide (dépôt vierge / bare).
INITIALISER_AVEC_README = True


def verifier_pre_requis() -> None:
    """Vérifie que la CLI GitHub 'gh' est installée et authentifiée."""
    if shutil.which("gh") is None:
        sys.exit(
            " Erreur : L'exécutable 'gh' est introuvable. "
            "Veuillez installer GitHub CLI."
        )

    auth_check = subprocess.run(
        ["gh", "auth", "status"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if auth_check.returncode != 0:
        sys.exit(
            " Erreur : GitHub CLI n'est pas authentifié.\n"
            "Veuillez exécuter 'gh auth login' au préalable."
        )


def creer_depot_prive(org: str, repo_name: str, auto_init: bool = False) -> bool:
    """Crée un dépôt privé dans l'organisation via l'API REST de GitHub.

    Retourne True si le dépôt a été créé, False s'il existait déjà.
    """
    endpoint = f"/orgs/{org}/repos"
    payload = {
        "name": repo_name,
        "private": True,
        "auto_init": auto_init,
        "description": f"Dépôt de projet étudiant pour {repo_name} (HAX712X)",
    }

    # Utilisation de 'gh api' avec passage de données JSON brutes
    cmd = [
        "gh",
        "api",
        "--method",
        "POST",
        "-H",
        "Accept: application/vnd.github+json",
        endpoint,
        "--input",
        "-",
    ]

    process = subprocess.run(
        cmd,
        input=json.dumps(payload),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if process.returncode == 0:
        return True

    # Analyse de l'erreur : si le dépôt existe déjà, GitHub renvoie une erreur 422
    erreur = process.stderr.lower()
    if "already exists" in erreur or "name already exists" in erreur:
        return False

    # Erreur inattendue
    print(f"    Échec création dépôt {repo_name} : {process.stderr.strip()}", file=sys.stderr)
    return False


def attacher_equipe_au_depot(
    org: str, team_slug: str, repo_name: str, permission: str = "push"
) -> bool:
    """Associe une équipe à un dépôt avec le niveau de permission souhaité.

    Niveaux acceptés : 'pull' (lecture), 'push' (écriture), 'admin'.
    """
    endpoint = f"/orgs/{org}/teams/{team_slug}/repos/{org}/{repo_name}"

    cmd = [
        "gh",
        "api",
        "--method",
        "PUT",
        "-H",
        "Accept: application/vnd.github+json",
        endpoint,
        "-f",
        f"permission={permission}",
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if process.returncode == 0:
        return True

    print(
        f"    Échec association équipe {team_slug} -> {repo_name} : {process.stderr.strip()}",
        file=sys.stderr,
    )
    return False


def main() -> None:
    print("=" * 70)
    print(" PHASE 2 : Provisionnement des dépôts et attribution des droits")
    print(f" Organisation : {ORG}")
    print(f" Nombre de groupes : {NB_GROUPES}")
    print("=" * 70)

    verifier_pre_requis()

    succes_creation = 0
    succes_droits = 0

    for i in range(1, NB_GROUPES + 1):
        team_slug = f"groupe-{i:02d}"
        repo_name = f"{PREFIXE_DEPOT}-{team_slug}"

        print(f"\n Traitement du Groupe {i:02d} :")

        # 1. Création du dépôt
        cree = creer_depot_prive(
            ORG, repo_name, auto_init=INITIALISER_AVEC_README
        )
        if cree:
            print(f"   [+] Dépôt créé : {ORG}/{repo_name} (Privé)")
            succes_creation += 1
        else:
            print(f"   [=] Dépôt existant : {ORG}/{repo_name} (Ignoré)")

        # 2. Attribution des permissions à l'équipe
        ok_perm = attacher_equipe_au_depot(
            ORG, team_slug, repo_name, permission="push"
        )
        if ok_perm:
            print(f"   [✓] Équipe '{team_slug}' associée avec droits d'écriture ('push')")
            succes_droits += 1
        else:
            print(f"   [✗] Problème d'attribution des droits pour '{team_slug}'")

    print("\n" + "=" * 70)
    print(" BILAN DE LA PHASE 2 :")
    print(f" • Dépôts créés / vérifiés : {NB_GROUPES}")
    print(f" • Équipes correctement liées : {succes_droits}/{NB_GROUPES}")
    print("=" * 70)
    print("\nProchaine étape : Configuration des workflows GitHub Actions (Phase 3).")


if __name__ == "__main__":
    main()