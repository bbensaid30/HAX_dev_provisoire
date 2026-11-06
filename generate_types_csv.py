"""Générateur de la matrice des types élémentaires pour PyArena (Socle 5 types)."""

from pathlib import Path
import pandas as pd

# Données contractuelles issues du Cahier des Charges PyArena
type_names = ["Normal", "Feu", "Eau", "Plante", "Électrik"]

# Lignes = Attaquant | Colonnes = Défenseur
multipliers = [
    [1.0, 1.0, 1.0, 1.0, 1.0],  # Normal
    [1.0, 0.5, 0.5, 2.0, 1.0],  # Feu
    [1.0, 2.0, 0.5, 0.5, 1.0],  # Eau
    [1.0, 0.5, 2.0, 0.5, 1.0],  # Plante
    [1.0, 1.0, 2.0, 0.5, 0.5],  # Électrik
]

df = pd.DataFrame(multipliers, index=type_names, columns=type_names)
df.index.name = "type"

output_path = Path("data_pyarena/types.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=True)

print(f"Fichier généré avec succès sous : {output_path.resolve()}")
