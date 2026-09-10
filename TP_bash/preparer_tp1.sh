#!/bin/bash
set -e

echo "=== Génération de l'environnement TP1 Linux ==="

# Nettoyage préalable
rm -rf tp1_linux tp1_linux.tar.gz

# 1. Structure Exercice 2 (Rangement automatisé)
mkdir -p tp1_linux/exercice_1/documents/images
mkdir -p tp1_linux/exercice_1/documents/textes
mkdir -p tp1_linux/exercice_1/vrac

touch tp1_linux/exercice_1/vrac/photo_01.png
touch tp1_linux/exercice_1/vrac/photo_02.png
touch tp1_linux/exercice_1/vrac/photo_03.png
touch tp1_linux/exercice_1/vrac/figure_test.png
touch tp1_linux/exercice_1/vrac/notes.txt
touch tp1_linux/exercice_1/vrac/rapport.txt
touch tp1_linux/exercice_1/vrac/script.py
touch tp1_linux/exercice_1/vrac/data.csv

# 2. Structure Exercice 3 (Permissions)
mkdir -p tp1_linux/exercice_2/scripts

cat << 'EOF' > tp1_linux/exercice_2/scripts/backup.sh
#!/bin/bash
echo "========================================================="
echo "[SUCCÈS] Le script de sauvegarde s'est exécuté sans erreur !"
echo "Tous les instantanés système ont été synchronisés."
echo "========================================================="
EOF
chmod 644 tp1_linux/exercice_2/scripts/backup.sh

cat << 'EOF' > tp1_linux/exercice_2/scripts/secret.conf
# Clé d'authentification API critique
API_SECRET_KEY="sk_live_99a7b8c2d1e4f5a6b7c8d9e0"
DB_PASSWORD="SuperSecretAdminPassword2026!"
EOF
chmod 666 tp1_linux/exercice_2/scripts/secret.conf

# 3. Structure Exercice 4 & Défis (Logs et Pipelines)
mkdir -p tp1_linux/exercice_3/logs

cat << 'EOF' > tp1_linux/exercice_3/logs/connexions.log
2026-09-10 08:01:12 user=alice ip=192.168.1.10 status=SUCCESS
2026-09-10 08:02:45 user=bob ip=192.168.1.15 status=FAILED
2026-09-10 08:05:01 user=charlie ip=192.168.1.20 status=SUCCESS
2026-09-10 08:12:33 user=bob ip=192.168.1.15 status=FAILED
2026-09-10 08:14:10 user=alice ip=192.168.1.10 status=SUCCESS
2026-09-10 08:20:00 user=eve ip=10.0.0.99 status=FAILED
2026-09-10 08:22:18 user=bob ip=192.168.1.15 status=FAILED
2026-09-10 08:30:45 user=charlie ip=192.168.1.20 status=SUCCESS
2026-09-10 08:31:02 user=eve ip=10.0.0.99 status=FAILED
2026-09-10 08:35:19 user=david ip=192.168.1.35 status=SUCCESS
2026-09-10 08:40:02 user=eve ip=10.0.0.99 status=FAILED
2026-09-10 08:42:15 user=alice ip=192.168.1.10 status=SUCCESS
2026-09-10 08:45:00 user=mallory ip=172.16.0.4 status=FAILED
2026-09-10 08:50:22 user=bob ip=192.168.1.15 status=SUCCESS
2026-09-10 08:55:10 user=david ip=192.168.1.35 status=SUCCESS
EOF

# 4. Structure Le Défi Récapitulatif
mkdir -p tp1_linux/defi/serveurs/alpha
mkdir -p tp1_linux/defi/serveurs/beta
mkdir -p tp1_linux/defi/serveurs/gamma

for s in alpha beta gamma; do
  for i in {1..15}; do
    echo "2026-09-10 host=$s pid=$((1000+i)) status=NOMINAL thread_count=4" > tp1_linux/defi/serveurs/$s/proc_$i.log
  done
done
echo "2026-09-10 host=beta pid=1007 ALERT INDICE_FINAL : [GIT/Dr-DOOM IS COMING SOON]" > tp1_linux/defi/serveurs/beta/proc_7.log

# 5. Compression tar.gz
tar -czf tp1_linux.tar.gz tp1_linux/
rm -rf tp1_linux

echo "-> Fichier 'tp1_linux.tar.gz' créé avec succès."
