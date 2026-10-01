"""Tests Oracle Enseignant - Validation stricte du contrat d'interface PyArena (HAX712X).

Ces tests vérifient la conformité de l'API publique sans dépendre de l'implémentation interne.
"""

import pytest


def test_oracle_base_fighter_est_abstraite():
    """Vérifie que BaseFighter est bien une classe abstraite non instanciable."""
    from pyarena.core.models import BaseFighter

    with pytest.raises(TypeError):
        BaseFighter()


def test_oracle_fighter_normalisation_niveau_50():
    """Contrôle les formules d'échelonnement normalisées au Niveau 50 :

    max_hp = hp_base + 60, Attack = attack_base + 5, Defense = defense_base + 5, Speed = speed_base + 5.
    """
    from pyarena.core.models import Fighter

    pikachu = Fighter(
        id=25,
        name="Pikachu",
        type_1="Électrik",
        type_2=None,
        hp_base=35,
        attack_base=55,
        defense_base=40,
        speed_base=90,
    )

    assert pikachu.max_hp == 95
    assert pikachu.hp == 95
    assert pikachu.attack == 60
    assert pikachu.defense == 45
    assert pikachu.speed == 95
    assert pikachu.is_alive() is True


def test_oracle_fighter_cycle_degats_et_ko():
    """Vérifie l'encapsulation de la vie, le bornage à 0 et la détection du K.-O."""
    from pyarena.core.models import Fighter

    bulbizarre = Fighter(
        id=1,
        name="Bulbizarre",
        type_1="Plante",
        type_2="Poison",
        hp_base=45,
        attack_base=49,
        defense_base=49,
        speed_base=45,
    )
    # max_hp = 105
    bulbizarre.take_damage(30)
    assert bulbizarre.hp == 75

    # Dégâts excessifs : les PV doivent être bornés à 0, pas de valeur négative
    bulbizarre.take_damage(200)
    assert bulbizarre.hp == 0
    assert bulbizarre.is_alive() is False


def test_oracle_exceptions_metier():
    """Valide l'arborescence des exceptions et l'interdiction d'agir pour une entité K.-O."""
    from pyarena.core.exceptions import FighterFaintedError, InvalidStatError, PyArenaException
    from pyarena.core.models import Fighter

    # Vérification de la hiérarchie d'héritage
    assert issubclass(FighterFaintedError, PyArenaException)
    assert issubclass(InvalidStatError, PyArenaException)

    # Statistique négative ou nulle interdite
    with pytest.raises(InvalidStatError):
        Fighter(
            id=4,
            name="Salamèche",
            type_1="Feu",
            type_2=None,
            hp_base=0,
            attack_base=52,
            defense_base=43,
            speed_base=65,
        )

    # Entité K.-O. subissant une action interdite
    carapuce = Fighter(
        id=7,
        name="Carapuce",
        type_1="Eau",
        type_2=None,
        hp_base=44,
        attack_base=48,
        defense_base=65,
        speed_base=43,
    )
    carapuce.take_damage(200)
    with pytest.raises(FighterFaintedError):
        carapuce.take_damage(10)


def test_oracle_simulate_battle_determinisme():
    """Vérifie la présence et le comportement contractuel du moteur simulate_battle."""
    from pyarena.core.engine import simulate_battle
    from pyarena.core.models import BattleResult, Fighter

    f1 = Fighter(25, "Pikachu", "Électrik", None, 35, 55, 40, 90)
    f2 = Fighter(7, "Carapuce", "Eau", None, 44, 48, 65, 43)

    res = simulate_battle(f1, f2, seed=42)
    assert isinstance(res, BattleResult)
    assert hasattr(res, "winner")
    assert hasattr(res, "loser")
    assert hasattr(res, "turns")
    assert hasattr(res, "remaining_hp")
    assert res.winner.is_alive() is True
    assert res.loser.is_alive() is False