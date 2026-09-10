# demo_rentree.py
# Commande pour lancer : streamlit run demo_rentree.py
import streamlit as st
import numpy as np
import plotly.express as px
import requests

st.set_page_config(page_title="Démo M1 - PyArena", page_icon="⚔️", layout="wide")

st.title("⚔️ M1 Dev Logiciel : Projet PyArena")
st.markdown("### *Moteur de Simulation Stochastique & Data Dashboard*")

# 1. Mini-base de données avec appels directs à l'API officielle
POKEMON_IDS = {
    "Pikachu": 25,
    "Dracaufeu (Charizard)": 6,
    "Tortank (Blastoise)": 9,
    "Florizarre (Venusaur)": 3
}

@st.cache_data
def load_pokemon_data(poke_id):
    """Récupère les données réelles et le sprite officiel via la PokéAPI."""
    url = f"https://pokeapi.co/api/v2/pokemon/{poke_id}"
    res = requests.get(url).json()
    stats = {s["stat"]["name"]: s["base_stat"] for s in res["stats"]}
    return {
        "name": res["name"].capitalize(),
        "sprite": res["sprites"]["front_default"],
        "hp": stats["hp"],
        "attack": stats["attack"],
        "defense": stats["defense"],
        "speed": stats["speed"]
    }

# Interface de sélection
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    choice_a = st.selectbox("Combattant A", list(POKEMON_IDS.keys()), index=0)
    data_a = load_pokemon_data(POKEMON_IDS[choice_a])
    st.image(data_a["sprite"], width=130)
    st.write(f"**PV:** {data_a['hp']} | **Attaque:** {data_a['attack']} | **Défense:** {data_a['defense']}")

with col_sel2:
    choice_b = st.selectbox("Combattant B", list(POKEMON_IDS.keys()), index=1)
    data_b = load_pokemon_data(POKEMON_IDS[choice_b])
    st.image(data_b["sprite"], width=130)
    st.write(f"**PV:** {data_b['hp']} | **Attaque:** {data_b['attack']} | **Défense:** {data_b['defense']}")

n_sims = st.slider("Nombre de simulations Monte-Carlo (parallélisées)", 100, 5000, 1000, step=100)

# Moteur de simulation stochastique vectorisé / rapide
def run_simulation(p1, p2, n):
    wins_p1 = 0
    turns_list = []
    for _ in range(n):
        hp1, hp2 = p1["hp"], p2["hp"]
        turn = 0
        while hp1 > 0 and hp2 > 0:
            turn += 1
            # Tour p1 -> p2 (formule avec variabilité uniforme et coup critique à 10%)
            crit1 = 1.5 if np.random.rand() < 0.10 else 1.0
            dmg1 = max(1, int((p1["attack"] / p2["defense"] * 15 + 2) * np.random.uniform(0.85, 1.0) * crit1))
            hp2 -= dmg1
            if hp2 <= 0:
                wins_p1 += 1
                turns_list.append(turn)
                break
            
            # Tour p2 -> p1
            crit2 = 1.5 if np.random.rand() < 0.10 else 1.0
            dmg2 = max(1, int((p2["attack"] / p1["defense"] * 15 + 2) * np.random.uniform(0.85, 1.0) * crit2))
            hp1 -= dmg2
            if hp1 <= 0:
                turns_list.append(turn)
                break
    return wins_p1 / n, turns_list

if st.button("🚀 Lancer l'estimation Monte-Carlo", type="primary"):
    winrate_a, turns = run_simulation(data_a, data_b, n_sims)
    
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Winrate {choice_a}", f"{winrate_a * 100:.1f} %")
    m2.metric(f"Winrate {choice_b}", f"{(1 - winrate_a) * 100:.1f} %")
    m3.metric("Durée moyenne d'un match", f"{np.mean(turns):.1f} tours")
    
    fig = px.histogram(x=turns, nbins=15, title="Distribution de la durée des combats (tours)",
                       labels={"x": "Nombre de tours", "y": "Effectif"}, color_discrete_sequence=["#3498db"])
    st.plotly_chart(fig, use_container_width=True)