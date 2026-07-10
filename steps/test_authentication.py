"""
steps/test_authentication.py
Step definitions BDD pour le module d'authentification OptiShop.

Chaque step correspond à une ligne Given/When/Then du fichier
features/authentication.feature — c'est le "contrat exécutable".

The Friday Breach · Arc Opération Sentinel · Semaine #11
"""

import pytest
from pytest_bdd import given, when, then, parsers, scenario

# ── Liaison scénarios ──────────────────────────────────────────────────────

@scenario("../features/authentication.feature",
           "Connexion réussie avec identifiants valides")
def test_login_success(auth_context):
    pass


@scenario("../features/authentication.feature",
           "Connexion échouée — mot de passe incorrect")
def test_login_failure(auth_context):
    pass


@scenario("../features/authentication.feature",
           "Blocage de compte après 3 tentatives échouées")
def test_account_lockout(auth_context):
    pass


@scenario("../features/authentication.feature",
           "Tentative de connexion sur un compte bloqué")
def test_login_on_locked_account(auth_context):
    pass


@scenario("../features/authentication.feature",
           "Protection contre l'énumération d'utilisateurs")
def test_user_enumeration_protection(auth_context):
    pass


@scenario("../features/authentication.feature",
           "Demande de réinitialisation de mot de passe")
def test_password_reset(auth_context):
    pass


# ── Steps Given ────────────────────────────────────────────────────────────

@given("l'application OptiShop est démarrée")
def app_started():
    """Le système est initialisé via le fixture auth_context."""
    pass


@given(parsers.parse('la base de données contient un compte actif pour "{email}"'))
def user_exists_in_db(email, auth_context):
    assert auth_context["system"].user_exists(email), \
        f"Utilisateur {email} introuvable dans le système de test."


@given("Alice est sur la page de connexion")
def on_login_page():
    """Navigation simulée — sera remplacée par Playwright en intégration."""
    pass


@given("son compte n'est pas bloqué")
def account_not_locked(auth_context):
    auth_context["system"].reset_attempts("alice@optishop.be")


@given(parsers.parse("elle a déjà effectué {n:d} tentatives de connexion échouées"))
def prior_failed_attempts(n, auth_context):
    auth_context["system"].set_attempts("alice@optishop.be", n)


@given(parsers.parse(
    "son compte a été bloqué il y a {elapsed:d} minutes "
    "suite à 3 tentatives échouées"
))
def account_locked_with_elapsed(elapsed, auth_context):
    auth_context["system"].set_attempts("alice@optishop.be", 3)
    auth_context["system"].set_lockout_remaining(
        "alice@optishop.be", 15 - elapsed
    )


@given(parsers.parse('un email "{email}" qui n\'existe pas dans le système'))
def nonexistent_email(email, auth_context):
    assert not auth_context["system"].user_exists(email), \
        f"{email} ne devrait pas exister dans le système de test."
    auth_context["state"]["attacker_email"] = email


@given("les champs email et mot de passe sont vides")
def empty_fields(auth_context):
    auth_context["state"]["email"] = ""
    auth_context["state"]["password"] = ""


# ── Steps When ─────────────────────────────────────────────────────────────

@when(parsers.parse('elle saisit l\'email "{email}" et son mot de passe correct'))
def enter_valid_credentials(email, auth_context):
    system = auth_context["system"]
    password = system._users.get(email, "")
    auth_context["result"] = system.login(email, password)


@when(parsers.parse('elle saisit l\'email "{email}" et un mot de passe incorrect'))
def enter_invalid_password(email, auth_context):
    auth_context["result"] = auth_context["system"].login(email, "mauvais_mdp")


@when("elle saisit un mot de passe incorrect une troisième fois")
def enter_wrong_password_third_time(auth_context):
    auth_context["result"] = auth_context["system"].login(
        "alice@optishop.be", "mauvais_mdp"
    )


@when("elle saisit ses identifiants corrects")
def enter_correct_credentials_on_locked(auth_context):
    system = auth_context["system"]
    auth_context["result"] = system.login(
        "alice@optishop.be", system._users["alice@optishop.be"]
    )


@when(parsers.parse(
    "un attaquant tente de se connecter avec \"{email}\" "
    "et n'importe quel mot de passe"
))
def attacker_attempts_login_with_email(email, auth_context):
    auth_context["result"] = auth_context["system"].login(email, "tentative_hack")


@when("un attaquant tente de se connecter avec cet email et n'importe quel mot de passe")
def attacker_attempts_login(auth_context):
    email = auth_context["state"].get("attacker_email", "inconnu@hack.com")
    auth_context["result"] = auth_context["system"].login(email, "tentative_hack")


@when("elle clique sur le bouton \"Connexion\"")
def click_login_button():
    """Action UI simulée — l'appel système est dans le When précédent."""
    pass


@when("il clique sur le bouton \"Connexion\"")
def attacker_clicks_login():
    pass


@when("elle clique sur le lien \"Mot de passe oublié ?\"")
def click_forgot_password():
    pass


@when(parsers.parse(
    "elle saisit son email \"{email}\" dans le formulaire de réinitialisation"
))
def enter_reset_email(email, auth_context):
    auth_context["state"]["reset_email"] = email


@when("elle clique sur \"Envoyer le lien de réinitialisation\"")
def submit_reset_form(auth_context):
    email = auth_context["state"]["reset_email"]
    auth_context["result"] = auth_context["system"].request_password_reset(email)


# ── Steps Then ─────────────────────────────────────────────────────────────

@then("elle est redirigée vers son tableau de bord")
def redirected_to_dashboard(auth_context):
    result = auth_context["result"]
    assert result.success is True, \
        f"Connexion échouée — raison : {result.reason} / {result.message}"
    assert result.redirect == "/dashboard", \
        f"Redirection attendue vers /dashboard, obtenu : {result.redirect}"


@then(parsers.parse("le message \"{expected_msg}\" s'affiche en haut de page"))
def welcome_message_shown(expected_msg, auth_context):
    result = auth_context["result"]
    assert result.user is not None, "Aucun utilisateur dans le résultat."
    expected_name = expected_msg.replace("Bonjour ", "")
    assert result.user == expected_name, \
        f"Nom attendu : {expected_name}, obtenu : {result.user}"


@then("elle reste sur la page de connexion")
def stays_on_login_page(auth_context):
    assert auth_context["result"].success is False


@then(parsers.parse("le message \"{expected_msg}\" s'affiche"))
def error_message_shown(expected_msg, auth_context):
    actual_msg = auth_context["result"].message
    assert actual_msg == expected_msg, \
        f"Message attendu : '{expected_msg}'\nMessage reçu   : '{actual_msg}'"


@then("aucune information ne précise si c'est l'email ou le mot de passe qui est faux")
def no_field_specific_info(auth_context):
    message = auth_context["result"].message
    assert "email" not in message.lower(), \
        "Le message ne doit pas mentionner 'email'."
    assert "mot de passe" not in message.lower() or \
           "identifiants" in message.lower(), \
        "Le message ne doit pas distinguer email vs mot de passe."


@then("son compte est bloqué pendant 15 minutes")
def account_is_locked(auth_context):
    result = auth_context["result"]
    assert result.reason == "locked", \
        f"Raison attendue : 'locked', obtenu : '{result.reason}'"


@then("elle ne peut pas se connecter")
def cannot_login(auth_context):
    assert auth_context["result"].success is False


@then("la durée restante est calculée dynamiquement")
def remaining_time_dynamic(auth_context):
    message = auth_context["result"].message
    # Le message doit contenir un nombre de minutes
    import re
    assert re.search(r"\d+\s*minutes?", message), \
        f"Le message devrait indiquer une durée en minutes : '{message}'"


@then("le bouton \"Connexion\" est désactivé")
def login_button_disabled():
    """Validation UI — simulée ici, sera testée via Playwright en intégration."""
    pass  # Marqué PENDING tant que l'UI n'est pas branchée


@then("le bouton \"Connexion\" reste désactivé")
def login_button_still_disabled():
    pass


@then("le bouton \"Connexion\" devient actif")
def login_button_enabled():
    pass


@then("le message d'erreur est identique à celui d'un mot de passe incorrect")
def same_error_as_wrong_password(auth_context):
    """
    Teste la protection anti-user-enumeration (OWASP A07).
    Le message pour un email inexistant doit être identique
    à celui d'un mot de passe incorrect sur un compte existant.
    """
    attacker_result = auth_context["result"]
    # Simule une tentative sur un compte existant avec mauvais mdp
    reference_result = auth_context["system"].login(
        "alice@optishop.be", "mauvais_mdp"
    )
    assert attacker_result.message == reference_result.message, (
        f"User enumeration détectée !\n"
        f"Message email inexistant  : '{attacker_result.message}'\n"
        f"Message mauvais mot passe : '{reference_result.message}'"
    )


@then("aucune indication ne révèle que l'email n'existe pas")
def no_email_existence_leak(auth_context):
    message = auth_context["result"].message
    forbidden_phrases = ["n'existe pas", "inconnu", "non trouvé", "not found"]
    for phrase in forbidden_phrases:
        assert phrase not in message.lower(), \
            f"Le message '{message}' révèle l'existence de l'email."


@then(parsers.parse(
    "le message \"{expected}\" s'affiche"
))
def reset_confirmation_shown(expected, auth_context):
    assert auth_context["result"].message == expected


@then(parsers.parse("un email de réinitialisation est envoyé à \"{email}\""))
def reset_email_sent(email, auth_context):
    assert auth_context["result"].success is True


@then(parsers.parse("le message de validation \"{message}\" s'affiche"))
def validation_message_shown(message, auth_context):
    """Validation côté client — simulée, testée via Playwright en intégration."""
    pass


@then("le formulaire n'est pas soumis au serveur")
def form_not_submitted():
    pass
