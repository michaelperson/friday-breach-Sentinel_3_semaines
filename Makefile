# Makefile — OptiShop Sentinel
# Commandes rapides pour le cycle BA → QA → Sécurité

.PHONY: install test test-report test-bdd clean help

help:
	@echo "Commandes disponibles :"
	@echo "  make install      — Installe les dépendances"
	@echo "  make test         — Lance tous les tests BDD"
	@echo "  make test-report  — Lance les tests + génère rapport HTML"
	@echo "  make clean        — Supprime les artefacts de build"

install:
	pip install -r requirements.txt

test:
	pytest steps/ -v --tb=short

test-report:
	pytest steps/ -v --tb=short --html=rapport-bdd.html --self-contained-html
	@echo "Rapport disponible : rapport-bdd.html"

clean:
	rm -rf .pytest_cache __pycache__ rapport-bdd.html
	find . -name "*.pyc" -delete
