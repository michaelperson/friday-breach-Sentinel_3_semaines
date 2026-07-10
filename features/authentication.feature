# authentication.feature
# OptiShop — Module Authentification
# The Friday Breach · Semaine #10 · Arc Opération Sentinel
#
# Ce fichier constitue le "contrat vivant" entre le BA, le QA et le client.
# Il est exécutable via pytest-bdd (S11) et servira de grille d'audit (S12).

Feature: Authentification utilisateur OptiShop
  En tant qu'utilisateur OptiShop
  Je veux pouvoir me connecter de manière sécurisée
  Afin d'accéder à mon tableau de bord et gérer mes commandes

  # Règles métier couvertes :
  #   R1 — Connexion email + mot de passe
  #   R2 — Message d'erreur générique (pas email vs mdp)
  #   R3 — Blocage après 3 tentatives échouées (15 min)
  #   R4 — Message de durée restante sur compte bloqué
  #   R5 — Redirection vers tableau de bord après succès
  #   R6 — Champs obligatoires, bouton désactivé si vide
  #   R7 — Réinitialisation de mot de passe par email
  #
  # Sécurité OWASP couverte :
  #   A07:2021 — Identification and Authentication Failures
  #   A03:2021 — Injection (scénario ajouté en S12)

  Background:
    Given l'application OptiShop est démarrée
      And la base de données contient un compte actif pour "alice@optishop.be"

  # ── HAPPY PATH ─────────────────────────────────────────────────────────────

  Scenario: Connexion réussie avec identifiants valides
    Given Alice est sur la page de connexion
      And son compte n'est pas bloqué
    When elle saisit l'email "alice@optishop.be" et son mot de passe correct
      And elle clique sur le bouton "Connexion"
    Then elle est redirigée vers son tableau de bord
      And le message "Bonjour Alice" s'affiche en haut de page

  # ── CAS D'ERREUR ───────────────────────────────────────────────────────────

  Scenario: Connexion échouée — mot de passe incorrect
    Given Alice est sur la page de connexion
    When elle saisit l'email "alice@optishop.be" et un mot de passe incorrect
      And elle clique sur le bouton "Connexion"
    Then elle reste sur la page de connexion
      And le message "Identifiants incorrects. Veuillez réessayer." s'affiche
      But aucune information ne précise si c'est l'email ou le mot de passe qui est faux

  Scenario: Blocage de compte après 3 tentatives échouées
    Given Alice est sur la page de connexion
      And elle a déjà effectué 2 tentatives de connexion échouées
    When elle saisit un mot de passe incorrect une troisième fois
      And elle clique sur le bouton "Connexion"
    Then son compte est bloqué pendant 15 minutes
      And le message "Compte temporairement bloqué. Réessayez dans 15 minutes." s'affiche
      And le bouton "Connexion" est désactivé

  Scenario: Tentative de connexion sur un compte bloqué
    Given Alice est sur la page de connexion
      And son compte a été bloqué il y a 5 minutes suite à 3 tentatives échouées
    When elle saisit ses identifiants corrects
      And elle clique sur le bouton "Connexion"
    Then elle ne peut pas se connecter
      And le message "Compte bloqué. Réessayez dans 10 minutes." s'affiche
      And la durée restante est calculée dynamiquement

  Scenario: Bouton Connexion désactivé si les champs sont vides
    Given Alice est sur la page de connexion
      And les champs email et mot de passe sont vides
    Then le bouton "Connexion" est désactivé
    When elle saisit uniquement l'email "alice@optishop.be"
    Then le bouton "Connexion" reste désactivé
    When elle saisit également un mot de passe
    Then le bouton "Connexion" devient actif

  Scenario: Demande de réinitialisation de mot de passe
    Given Alice est sur la page de connexion
    When elle clique sur le lien "Mot de passe oublié ?"
      And elle saisit son email "alice@optishop.be" dans le formulaire de réinitialisation
      And elle clique sur "Envoyer le lien de réinitialisation"
    Then le message "Un email vous a été envoyé avec les instructions." s'affiche
      And un email de réinitialisation est envoyé à "alice@optishop.be"

  # ── SÉCURITÉ ───────────────────────────────────────────────────────────────

  Scenario: Protection contre l'énumération d'utilisateurs
    Given un email "attaquant@hack.com" qui n'existe pas dans le système
    When un attaquant tente de se connecter avec cet email et n'importe quel mot de passe
      And il clique sur le bouton "Connexion"
    Then le message d'erreur est identique à celui d'un mot de passe incorrect
      And aucune indication ne révèle que l'email n'existe pas

  # ── SCENARIO OUTLINE ───────────────────────────────────────────────────────

  Scenario Outline: Validation des formats d'email invalides
    Given Alice est sur la page de connexion
    When elle saisit "<email_invalide>" dans le champ email
      And elle saisit un mot de passe quelconque
    Then le message de validation "<message>" s'affiche
      And le formulaire n'est pas soumis au serveur

    Examples:
      | email_invalide    | message                          |
      | alice             | Format d'email invalide          |
      | alice@            | Format d'email invalide          |
      | @optishop.be      | Format d'email invalide          |
      | alice@optishop    | Format d'email invalide          |
      |                   | L'email est obligatoire          |
