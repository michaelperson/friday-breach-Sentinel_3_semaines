"""
app.py — OptiShop Auth · VERSION DÉLIBÉRÉMENT VULNÉRABLE
=========================================================
⚠️  NE JAMAIS DÉPLOYER EN PRODUCTION ⚠️

Ce fichier est le terrain d'entraînement pour la Semaine 12
de l'arc Opération Sentinel — Audit Sécurité OWASP.

Vulnérabilités introduites intentionnellement :
  VULN-01 · Clé secrète hardcodée               → OWASP A02
  VULN-02 · Mots de passe en clair (pas de hash) → OWASP A02
  VULN-03 · Injection SQL (concaténation)         → OWASP A03
  VULN-04 · User Enumeration (messages différents)→ OWASP A07
  VULN-05 · Absence de rate limiting / brute force→ OWASP A07
  VULN-06 · Credentials acceptés en GET (URL)     → OWASP A02
  VULN-07 · Messages d'erreur verbeux (SQL exposé)→ OWASP A05
  VULN-08 · debug=True en production              → OWASP A05

The Friday Breach · Arc Opération Sentinel · Semaine #12
"""

from flask import Flask, request, jsonify, session
import sqlite3

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# 🚨 VULN-01 : Clé secrète hardcodée dans le code source
#    Impact  : quiconque lit le code peut forger des sessions
#    Fix     : secret_key = os.environ["SECRET_KEY"]
# ─────────────────────────────────────────────────────────────
app.secret_key = "optishop2024"


def get_db():
    """Retourne une connexion SQLite en mémoire (réinitialisée au démarrage)."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            name     TEXT    NOT NULL,
            locked   INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ─────────────────────────────────────────────────────────
    # 🚨 VULN-02 : Mots de passe stockés en clair
    #    Impact  : une fuite DB expose tous les mots de passe
    #    Fix     : bcrypt.hashpw() ou argon2
    # ─────────────────────────────────────────────────────────
    conn.execute("""
        INSERT OR IGNORE INTO users (id, email, password, name) VALUES
        (1, 'alice@optishop.be', 'MotDePasse123!', 'Alice'),
        (2, 'bob@optishop.be',   'bob123',         'Bob'),
        (3, 'admin@optishop.be', 'admin',           'Admin')
    """)

    conn.commit()
    return conn


db = get_db()


# ═══════════════════════════════════════════════════════════════
# ENDPOINT : POST /login (et GET — voir VULN-06)
# ═══════════════════════════════════════════════════════════════
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Endpoint de connexion.

    Accepte les paramètres via :
      - POST body (application/x-www-form-urlencoded)
      - GET query string  ← VULN-06

    Exemple d'appel légitime :
      curl -X POST http://localhost:5000/login \\
           -d "email=alice@optishop.be&password=MotDePasse123!"

    Exemple d'appel vulnérable (VULN-06) :
      curl "http://localhost:5000/login?email=alice@optishop.be&password=MotDePasse123!"
    """

    # Récupération des paramètres (POST ou GET)
    email    = request.args.get("email")    or request.form.get("email",    "")
    password = request.args.get("password") or request.form.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Les champs email et mot de passe sont obligatoires."
        }), 400

    # ─────────────────────────────────────────────────────────
    # 🚨 VULN-03 : Injection SQL par concaténation de chaînes
    #    Impact  : bypass d'authentification, extraction de données
    #    Fix     : cursor.execute("... WHERE email=?", (email,))
    #
    #    Payload de test :
    #      email    = ' OR '1'='1' --
    #      password = anything
    # ─────────────────────────────────────────────────────────
    query = (
        f"SELECT id, email, name, locked FROM users "
        f"WHERE email='{email}' AND password='{password}'"
    )

    try:
        cursor = db.execute(query)
        user = cursor.fetchone()
    except sqlite3.OperationalError as e:
        # ─────────────────────────────────────────────────────
        # 🚨 VULN-07 : Erreur verbose — expose la requête SQL
        #    Impact  : aide l'attaquant à affiner son payload
        #    Fix     : logger l'erreur côté serveur, retourner
        #              un message générique au client
        # ─────────────────────────────────────────────────────
        return jsonify({
            "success": False,
            "error":   str(e),
            "query":   query,    # ← ne JAMAIS exposer ça en prod
            "message": "Erreur base de données."
        }), 500

    # ─────────────────────────────────────────────────────────
    # 🚨 VULN-05 : Absence de rate limiting / brute force
    #    Impact  : un attaquant peut tenter 10 000 mots de passe
    #              sans aucun blocage ni délai
    #    Fix     : compteur de tentatives + blocage temporaire
    #              (la règle R3 du cahier des charges !)
    # ─────────────────────────────────────────────────────────

    if user:
        user_id, user_email, user_name, locked = user

        if locked:
            return jsonify({
                "success": False,
                "message": "Compte bloqué. Contactez le support."
            }), 403

        session["user_id"]   = user_id
        session["user_email"] = user_email
        return jsonify({
            "success":  True,
            "user":     user_name,
            "redirect": "/dashboard"
        }), 200

    # ─────────────────────────────────────────────────────────
    # 🚨 VULN-04 : User Enumeration — messages différents
    #    Impact  : un attaquant peut distinguer si un email
    #              existe ou non dans la base
    #    Fix     : toujours retourner "Identifiants incorrects."
    # ─────────────────────────────────────────────────────────
    email_exists = db.execute(
        f"SELECT 1 FROM users WHERE email='{email}'"
    ).fetchone()

    if not email_exists:
        return jsonify({
            "success": False,
            "message": "Aucun compte associé à cet email."   # ← message révélateur
        }), 401

    return jsonify({
        "success": False,
        "message": "Mot de passe incorrect."                 # ← message différent
    }), 401


# ═══════════════════════════════════════════════════════════════
# ENDPOINT : GET /dashboard
# ═══════════════════════════════════════════════════════════════
@app.route("/dashboard")
def dashboard():
    """Tableau de bord — accès restreint aux utilisateurs authentifiés."""
    if "user_id" not in session:
        return jsonify({"error": "Non autorisé. Veuillez vous connecter."}), 401

    return jsonify({
        "message":  f"Bienvenue sur votre tableau de bord, utilisateur #{session['user_id']}",
        "email":    session.get("user_email"),
        "sections": ["Mes commandes", "Mon profil", "Facturation"]
    })


# ═══════════════════════════════════════════════════════════════
# ENDPOINT : POST /reset-password
# ═══════════════════════════════════════════════════════════════
@app.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Demande de réinitialisation de mot de passe (R7).
    Note : cet endpoint est correctement implémenté (anti-enumeration).
    """
    email = request.form.get("email", "")
    if not email:
        return jsonify({"success": False, "message": "Email obligatoire."}), 400

    # Message uniforme — pas de user enumeration ici (contrairement à /login)
    return jsonify({
        "success": True,
        "message": "Un email vous a été envoyé avec les instructions."
    })


# ═══════════════════════════════════════════════════════════════
# ENDPOINT : GET /health
# ═══════════════════════════════════════════════════════════════
@app.route("/health")
def health():
    """Health check — vérifie que l'app et la DB sont opérationnelles."""
    try:
        db.execute("SELECT 1")
        return jsonify({"status": "ok", "db": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# LANCEMENT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │  🔴 OptiShop Auth — VERSION VULNÉRABLE (TRAINING ONLY)  │
    │                                                         │
    │  Endpoints disponibles :                                │
    │    POST /login           → Connexion                    │
    │    GET  /login?email=... → ⚠️  VULN-06 (GET creds)      │
    │    GET  /dashboard       → Tableau de bord              │
    │    POST /reset-password  → Réinitialisation             │
    │    GET  /health          → Health check                 │
    │                                                         │
    │  Comptes de test :                                      │
    │    alice@optishop.be / MotDePasse123!                   │
    │    bob@optishop.be   / bob123                           │
    │    admin@optishop.be / admin                            │
    │                                                         │
    │  The Friday Breach · Semaine 12 · Audit OWASP           │
    └─────────────────────────────────────────────────────────┘
    """)

    # ─────────────────────────────────────────────────────────
    # 🚨 VULN-08 : debug=True expose la console Werkzeug
    #    Impact  : exécution de code arbitraire si accessible
    #    Fix     : debug=False + variable d'environnement
    # ─────────────────────────────────────────────────────────
    app.run(host="0.0.0.0", port=5000, debug=True)
