# Informations du Projet

## Nom du Projet
Outil sécurité documents par l'IA (IA Doc Security Checker)

## Date de création/mise à jour
01/07/2026

## Description
Outil web statique permettant aux auto-entrepreneurs, TPE et PME d'évaluer le degré de sécurité d'un type de document avant de le déposer sur une plateforme d'IA (ChatGPT, Claude, DeepSeek, Mistral, etc.). L'outil classe les documents par secteur (compta, commercial, juridique, RH, etc.), indique le niveau de risque, où vont les données (US, FR, EU, Chine), et recommande les modèles appropriés selon la sensibilité — y compris les modèles locaux (Ollama) pour les documents critiques.

## Architecture

### Version unique (publique, sans login)
Tableau de bord interactif — sélection secteur → type de document → niveau de risque + tableau des modèles IA + recommandation. Moteur de recherche par mot-clé. Bilingue FR/EN.

### Stack technique
- **Frontend** : Astro 7+ statique, Tailwind CSS 4, bilingue FR/EN (bouton toggle)
- **Déploiement** : Vercel (static)
- **Pas de backend** : tout est calculé côté client à partir de fichiers JSON statiques

### Base de données (fichiers JSON statiques)
- `src/data/sectors.fr.json` / `sectors.en.json` — 14 secteurs, ~90 types de documents + niveaux de sensibilité
- `src/data/models.fr.json` / `models.en.json` — 17 modèles IA (juridiction, rétention, entraînement, risque)
- `src/data/recommendations.json` — matrice de recommandation (sensibilité × modèle)

### Niveaux de sensibilité des documents
- 🟢 Faible : pas de données personnelles, informations publiques
- 🟡 Moyen : données commerciales/financières non sensibles
- 🔴 Élevé : données personnelles RGPD, informations financières détaillées
- 🔴🔴 Critique : secrets industriels, santé, credentials → modèles locaux uniquement

### Modèles IA référencés
ChatGPT (free/plus/enterprise), Claude, Google Gemini (free/workspace), Mistral API/Le Chat, DeepSeek, Qwen, Kimi, GLM, Microsoft 365 Copilot, Ollama Local, llama.cpp Local, Azure OpenAI, AWS Bedrock.

## Structure du projet
```
src/
  data/           — JSON data (sectors, models, recommendations)
  i18n/           — ui.json + index.ts (FR/EN)
  layouts/        — Layout.astro (header, nav, footer, titre dynamique)
  pages/
    index.astro   — redirect / → /fr/
    [lang]/
      index.astro   — page d'accueil
      tableau.astro — sélection secteur + document
      resultat.astro — résultat + modèles recommandés
      a-propos.astro — méthodologie + sources
  styles/         — global.css (Tailwind + responsive tables)
```

## Conventions & règles de développement

### Bilinguisme FR/EN
- Bouton toggle FR/EN dans le header
- Fichiers JSON en double : `.fr.json` / `.en.json`
- Traductions d'interface dans `src/i18n/ui.json`
- Préférence stockée dans `localStorage`, FR par défaut

## Informations Git
### Branche actuelle
```
main
```
