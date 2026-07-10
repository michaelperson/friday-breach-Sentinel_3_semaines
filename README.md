# OptiShop — Sentinel Auth

Dépôt de référence pour l'arc **Opération Sentinel** du programme *The Friday Breach*.

## Contexte

Ce dépôt couvre le cycle complet BA → QA → Sécurité appliqué au module d'authentification de la marketplace OptiShop.

| Semaine | Branche | Contenu |
|---|---|---|
| S10 — BDD/Gherkin | `Features/Semaine10` | Scénarios d'acceptance (`authentication.feature`) |
| S11 — Automatisation | `Features/Semaine11` | Step definitions pytest-bdd |
| S12 — Audit OWASP | `dev` *(base avant S12)* | Code intégré + app vulnérable à venir |

## Structure

```
├── features/
│   └── authentication.feature   # Contrat vivant BA ↔ QA ↔ Client
├── src/
│   └── auth_system.py           # Couche d'abstraction (swappable)
├── steps/
│   └── test_authentication.py   # Step definitions pytest-bdd
├── conftest.py                  # Fixtures partagées
├── pytest.ini                   # Configuration pytest
├── requirements.txt             # Dépendances
└── Makefile                     # Commandes rapides
```

## Démarrage rapide

```bash
# Installer les dépendances
make install

# Lancer les tests
make test

# Générer le rapport HTML
make test-report
```

## Branches

- **`Features/Semaine10`** — Semaine 10 : scénarios Gherkin uniquement
- **`Features/Semaine11`** — Semaine 11 : automatisation complète
- **`dev`** — État intégré avant le challenge S12 (audit OWASP)
- **`main`** — Branche stable (état validé)

## Règles métier couvertes

| Règle | Description | Scénario |
|---|---|---|
| R1 | Connexion email + mot de passe | Connexion réussie |
| R2 | Message d'erreur générique | Connexion échouée |
| R3 | Blocage après 3 tentatives | Blocage de compte |
| R4 | Durée restante affichée | Compte bloqué |
| R5 | Redirection tableau de bord | Connexion réussie |
| R6 | Champs obligatoires | Bouton désactivé |
| R7 | Réinitialisation par email | Mot de passe oublié |
| SEC | Protection user enumeration | OWASP A07 |

---
*The Friday Breach · Arc Opération Sentinel · L'Architecte · 2026*
