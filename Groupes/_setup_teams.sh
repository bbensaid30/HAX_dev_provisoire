#!/usr/bin/env bash
set -e

# ==============================================================================
# Configuration
# ==============================================================================
ORG="m1-ssd-2026"
CSV_FILE="promotions_2026.csv"
NB_GROUPES=8

# ==============================================================================
# Vérifications préalables
# ==============================================================================
if ! command -v gh >/dev/null 2>&1; then
    echo "Erreur : la CLI GitHub (gh) n'est pas installée sur cette machine." >&2
    exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "Erreur : la CLI GitHub n'est pas authentifiée. Lance 'gh auth login' avant d'exécuter ce script." >&2
    exit 1
fi

if [ ! -f "$CSV_FILE" ]; then
    echo "Erreur : le fichier '\(CSV_FILE' est introuvable dans le répertoire courant (\)(pwd))." >&2
    exit 1
fi

# ==============================================================================
# Phase 1.1 : Création des équipes (Teams)
# ==============================================================================
echo "=== [1/2] Création des équipes sur GitHub (groupe-01 à groupe-${NB_GROUPES}) ==="
for i in \((seq -w 1 "\)NB_GROUPES"); do
    TEAM_SLUG="groupe-${i}"
    echo " -> Initialisation de l'équipe : ${TEAM_SLUG}"
    gh api --method POST \
        -H "Accept: application/vnd.github+json" \
        "/orgs/${ORG}/teams" \
        -f name="${TEAM_SLUG}" \
        -f privacy="closed" >/dev/null 2>&1 || true
done

# ==============================================================================
# Phase 1.2 : Inscription et affectation des étudiants
# ==============================================================================
echo ""
echo "=== [2/2] Affectation des étudiants depuis '${CSV_FILE}' ==="

# tail -n +2 ignore la première ligne d'en-tête (groupe,github_user)
tail -n +2 "\(CSV_FILE" | while IFS=',' read -r GROUPE USERNAME || [ -n "\)GROUPE" ]; do
    # Nettoyage natif : suppression des espaces, tabulations et sauts de ligne Windows (\r)
    GROUPE="\({GROUPE//[\)'\r\n\t ']/}"
    USERNAME="\({USERNAME//[\)'\r\n\t ']/}"

    # Sauter les lignes vides éventuelles
    if [ -z "\(GROUPE" ] || [ -z "\)USERNAME" ]; then
        continue
    fi

    echo " -> Ajout de \({USERNAME} dans l'équipe\){GROUPE}"

    # 1. Invitation / ajout du compte à l'organisation GitHub
    gh api --method PUT \
        -H "Accept: application/vnd.github+json" \
        "/orgs/\({ORG}/memberships/\){USERNAME}" \
        -f role="member" >/dev/null 2>&1 || true

    # 2. Rattachement du compte à son équipe dédiée
    gh api --method PUT \
        -H "Accept: application/vnd.github+json" \
        "/orgs/\({ORG}/teams/\){GROUPE}/memberships/${USERNAME}" \
        -f role="member" >/dev/null 2>&1 || true
done

echo ""
echo "=== Phase 1 terminée : toutes les équipes et inscriptions sont opérationnelles. ==="