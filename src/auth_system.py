"""
auth_system.py
OptiShop — Couche d'abstraction du système d'authentification.

Cette classe est le "driver" utilisé par les step definitions BDD.
En test : elle simule le système en mémoire.
En intégration : elle sera remplacée par des appels HTTP réels.

The Friday Breach · Arc Opération Sentinel · Semaine #11
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AuthResult:
    """Résultat normalisé d'une tentative d'authentification."""
    success: bool
    reason: Optional[str] = None      # "locked" | "invalid" | "unknown_email"
    message: str = ""
    user: Optional[str] = None
    redirect: Optional[str] = None


class AuthSystem:
    """
    Simulation du système d'authentification OptiShop.

    Implémente les règles R1-R7 définies dans authentication.feature.
    Peut être swappé par un client HTTP pour les tests d'intégration.

    Usage:
        auth = AuthSystem()
        result = auth.login("alice@optishop.be", "MotDePasse123!")
        assert result.success
    """

    LOCKOUT_THRESHOLD: int = 3
    LOCKOUT_MESSAGE: str = "Compte temporairement bloqué. Réessayez dans 15 minutes."
    INVALID_MESSAGE: str = "Identifiants incorrects. Veuillez réessayer."

    def __init__(self):
        # Utilisateurs de test — en prod, remplacer par un appel DB
        self._users: dict[str, str] = {
            "alice@optishop.be": "MotDePasse123!",
            "bob@optishop.be":   "BobSecret456!",
        }
        self._failed_attempts: dict[str, int] = {}
        self._lockout_remaining: dict[str, int] = {}

    # ── Authentification ───────────────────────────────────────────────────

    def login(self, email: str, password: str) -> AuthResult:
        """
        Tente une authentification.

        Règles appliquées :
          R1  — vérification email + password
          R2  — message d'erreur générique (anti user-enumeration)
          R3  — blocage après LOCKOUT_THRESHOLD tentatives échouées
          R4  — message de durée restante sur compte bloqué
          R5  — redirect vers /dashboard en cas de succès
        """
        if self.is_locked(email):
            remaining = self._lockout_remaining.get(email, 15)
            return AuthResult(
                success=False,
                reason="locked",
                message=f"Compte bloqué. Réessayez dans {remaining} minutes.",
            )

        # Vérification credentials (R2 : même message, email connu ou non)
        if email not in self._users or self._users[email] != password:
            self._failed_attempts[email] = self._failed_attempts.get(email, 0) + 1

            if self._failed_attempts[email] >= self.LOCKOUT_THRESHOLD:
                self._lockout_remaining[email] = 15
                return AuthResult(
                    success=False,
                    reason="locked",
                    message=self.LOCKOUT_MESSAGE,
                )

            return AuthResult(
                success=False,
                reason="invalid",
                message=self.INVALID_MESSAGE,
            )

        # Succès (R5)
        self._failed_attempts[email] = 0
        name = email.split("@")[0].capitalize()
        return AuthResult(
            success=True,
            user=name,
            redirect="/dashboard",
        )

    # ── Gestion des états ──────────────────────────────────────────────────

    def is_locked(self, email: str) -> bool:
        """Retourne True si le compte est en état de blocage."""
        return self._failed_attempts.get(email, 0) >= self.LOCKOUT_THRESHOLD

    def reset_attempts(self, email: str) -> None:
        """Remet le compteur de tentatives à zéro. Utilisé dans les fixtures."""
        self._failed_attempts[email] = 0
        self._lockout_remaining.pop(email, None)

    def set_attempts(self, email: str, count: int) -> None:
        """Force le compteur à une valeur donnée. Utilisé dans les fixtures."""
        self._failed_attempts[email] = count

    def set_lockout_remaining(self, email: str, minutes: int) -> None:
        """Définit la durée restante de blocage. Utilisé dans les fixtures."""
        self._lockout_remaining[email] = minutes

    def user_exists(self, email: str) -> bool:
        """Vérifie si un utilisateur existe (usage interne uniquement)."""
        return email in self._users

    def request_password_reset(self, email: str) -> AuthResult:
        """
        Déclenche un email de réinitialisation de mot de passe (R7).
        Retourne toujours le même message, que l'email existe ou non.
        """
        # Anti-enumeration : même réponse si email inconnu
        return AuthResult(
            success=True,
            message="Un email vous a été envoyé avec les instructions.",
        )
