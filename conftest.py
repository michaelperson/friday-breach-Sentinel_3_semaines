"""
conftest.py
Configuration pytest-bdd et fixtures partagées.

Le fixture `auth_context` isole l'état de chaque scénario :
chaque test repart avec un AuthSystem vierge, évitant les interférences.

The Friday Breach · Arc Opération Sentinel · Semaine #11
"""

import pytest
from src.auth_system import AuthSystem


@pytest.fixture
def auth_context():
    """
    Contexte partagé injecté dans chaque step definition.

    Structure :
      {
        "system":  AuthSystem  — instance fraîche par scénario
        "result":  AuthResult  — résultat de la dernière action
        "state":   dict        — données arbitraires inter-steps
      }

    Usage dans un step :
        @given("Alice est sur la page de connexion")
        def on_login_page(auth_context):
            pass  # le contexte est disponible si besoin
    """
    return {
        "system": AuthSystem(),
        "result": None,
        "state":  {},
    }
