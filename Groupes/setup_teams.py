#!/usr/bin/env python3
import csv
import subprocess
import sys

ORG = "m1-ssd-2026"
CSV_FILE = "promotions_2026.csv"
NB_GROUPES = 8


def run_gh_api(method: str, endpoint: str, **fields) -> None:
    """Exécute une commande gh api via subprocess."""
    cmd = [
        "gh",
        "api",
        "--method",
        method,
        "-H",
        "Accept: application/vnd.github+json",
        endpoint,
    ]
    for key, val in fields.items():
        cmd.extend(["-f", f"{key}={val}"])

    # On ignore les erreurs si l'équipe ou le membre existe déjà
    subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
    )


def main() -> None:
    # 1. Création des équipes
    print(f"--- [1/2] Création des {NB_GROUPES} équipes sur GitHub ---")
    for i in range(1, NB_GROUPES + 1):
        team_slug = f"groupe-{i:02d}"
        print(f" -> Création de l'équipe : {team_slug}")
        run_gh_api(
            "POST", f"/orgs/{ORG}/teams", name=team_slug, privacy="closed"
        )

    # 2. Lecture du fichier CSV et inscription
    print(f"\n--- [2/2] Inscription des étudiants depuis {CSV_FILE} ---")
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Sauter la ligne d'en-tête (groupe, github_user)
            header = next(reader, None)

            for row in reader:
                if not row or len(row) < 2:
                    continue
                groupe = row[0].strip()
                username = row[1].strip()

                if groupe and username:
                    print(f" -> Inscription de {username} dans {groupe}")
                    # Invitation organisation
                    run_gh_api(
                        "PUT",
                        f"/orgs/{ORG}/memberships/{username}",
                        role="member",
                    )
                    # Ajout à l'équipe
                    run_gh_api(
                        "PUT",
                        f"/orgs/{ORG}/teams/{groupe}/memberships/{username}",
                        role="member",
                    )

    except FileNotFoundError:
        print(f"Erreur : le fichier {CSV_FILE} est introuvable.", file=sys.stderr)
        sys.exit(1)

    print("\nInitialisation terminée avec succès !")


if __name__ == "__main__":
    main()