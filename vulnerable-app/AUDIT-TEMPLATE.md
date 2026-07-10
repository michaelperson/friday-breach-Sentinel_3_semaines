# Rapport d'Audit Sécurité — OptiShop · Module Authentification
**Date :** _________________
**Auditeur :** _________________
**Version auditée :** 1.0.0-vulnerable
**Statut :** ⛔ / ✅ _(à compléter)_

---

## Résumé Exécutif

> _(2-3 phrases max pour un manager non-technique.
> Exemple : "L'audit révèle N vulnérabilités dont X critiques.
> Le go-live est bloqué/autorisé sous conditions.")_

---

## Environnement de test

| Élément | Valeur |
|---|---|
| URL cible | `http://localhost:5000` |
| Méthode | Test manuel + scanner _(OWASP ZAP / curl)_ |
| Durée | 60 minutes |
| Authentifiants de test | alice@optishop.be / MotDePasse123! |

---

## Findings

> Copie et complète un bloc par vulnérabilité trouvée.

---

### FINDING-01 · _[Titre de la vulnérabilité]_

**Sévérité :** 🔴 CRITICAL / 🟠 HIGH / 🟡 MEDIUM / 🟢 LOW
**Catégorie OWASP :** A0X:2021 — _[Nom]_
**Endpoint affecté :** `[GET|POST] /endpoint`

**Description :**
> _(Expliquer le problème en 2-3 phrases, lisible par un non-technicien)_

**Preuve (Proof of Concept) :**
```
Commande / payload utilisé :
  [commande curl ou payload]

Résultat obtenu :
  [output observé]

Résultat attendu :
  [ce qui devrait se passer]
```

**Impact :**
> _(Que peut faire un attaquant grâce à cette faille ?)_

**Recommandation :**
```python
# ❌ Code vulnérable
[extrait de code problématique]

# ✅ Code corrigé
[extrait de code corrigé]
```

---

### FINDING-02 · _[Titre]_

**Sévérité :**
**Catégorie OWASP :**
**Endpoint affecté :**

**Description :**

**Preuve :**
```
```

**Impact :**

**Recommandation :**

---

### FINDING-03 · _[Titre]_

_(Ajouter autant de findings que nécessaire)_

---

## Matrice de Risque

| # | Finding | Sévérité | Effort correction | Priorité |
|---|---|---|---|---|
| 01 | | | | P0 / P1 / P2 |
| 02 | | | | |
| 03 | | | | |

---

## Tests effectués

| Test | Résultat | OWASP |
|---|---|---|
| SQL Injection `' OR '1'='1' --` | ✅ Vulnérable / 🛡️ Protégé | A03 |
| User Enumeration (messages différents) | | A07 |
| Brute Force (10 tentatives sans blocage) | | A07 |
| Credentials via GET (URL) | | A02 |
| Erreur verbose (SQL exposé) | | A05 |
| Clé secrète hardcodée | | A02 |
| Mots de passe en clair | | A02 |
| debug=True en production | | A05 |

---

## Conclusion

**Statut go-live :** ⛔ Bloqué / ✅ Autorisé sous conditions

**Findings bloquants (P0) :**
- _[liste]_

**Findings à corriger avant J+30 (P1) :**
- _[liste]_

**Améliorations recommandées (P2) :**
- _[liste]_

**Re-audit requis :** Oui / Non

---

*The Friday Breach · Arc Opération Sentinel · Semaine #12*
*Auditeur : _________________ · Date : _________________*
