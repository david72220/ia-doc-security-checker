# Informations du Projet

## Nom du Projet
Outil sécurité documents par l'IA (IA Doc Security Checker)

## Date de création/mise à jour
30/06/2026

## Description
Outil web permettant aux auto-entrepreneurs, TPE et PME d'évaluer le degré de sécurité d'un document type avant de le déposer sur une plateforme d'IA (ChatGPT, Claude, DeepSeek, Mistral, etc.). L'outil classe les documents par secteur (compta, commercial, juridique, RH, etc.), indique le niveau de risque, où vont les données (US, FR, EU, Chine), et recommande les modèles appropriés selon la sensibilité — y compris les modèles locaux (Ollama) pour les documents critiques.

## Architecture

### Deux versions
1. **Version publique (sans login)** : tableau de bord interactif — sélection secteur → type de document → niveau de risque + tableau des modèles IA + recommandation. Moteur de recherche par mot-clé.
2. **Version authentifiée (user/mdp)** : upload de document analysé sur le VPS via Ollama local, suppression immédiate après analyse. Accès compris dans les formations payantes.

### Stack technique
- **Frontend** : Astro 6+ statique, Tailwind CSS, bilingue FR/EN (bouton toggle)
- **Backend analyse** : FastAPI sur VPS Hostinger (72.62.21.38), Ollama local (qwen3.5:9b)
- **Authentification** : JWT, base utilisateurs dans Notion (API Notion)
- **Déploiement** : Frontend sur Vercel, API sur VPS via Traefik
- **Domaine** : nouveau domaine à créer

### Base de données
- `src/data/sectors.fr.json` / `sectors.en.json` — secteurs + types de documents + niveaux de sensibilité
- `src/data/models.fr.json` / `models.en.json` — catalogue des modèles IA (juridiction, rétention, entraînement, risque)
- `src/data/recommendations.json` — matrice de recommandation (sensibilité × modèle)
- Base Notion "Utilisateurs" pour l'authentification (Nom, Email, Password hash, Formation, Actif)

### Niveaux de sensibilité des documents
- 🟢 Faible : pas de données personnelles, informations publiques
- 🟡 Moyen : données commerciales/financières non sensibles
- 🔴 Élevé : données personnelles RGPD, informations financières détaillées
- 🔴🔴 Critique : secrets industriels, santé, credentials, données clients massives → modèles locaux uniquement

### Modèles IA référencés
ChatGPT (free/plus/enterprise), Claude, Google Gemini, Mistral/Le Chat, DeepSeek, Qwen, Kimi, GLM, Ollama Cloud, Ollama Local, Azure OpenAI, AWS Bedrock.

## Structure du projet
```
./.git
./Claude.md
./astro.config.mjs
./package.json
./tsconfig.json
./public/
./src/
```
> Voir le plan détaillé : ~/.hermes/plans/2026-06-30_143000-ai-doc-security-checker.md

## Fichiers importants
- `Claude.md` — ce fichier (contexte projet)
- Plan d'implémentation : `~/.hermes/plans/2026-06-30_143000-ai-doc-security-checker.md`

## Informations Git
### Branche actuelle
```
main
```

## Conventions & règles de développement

### Workflow David (strict plan-first)
1. **Plan avant exécution** — ne jamais commencer à coder sans plan validé
2. **Vérification stricte** : write → commit → push → build → deploy → verify
3. **Confirmation explicite** avant toute opération destructive
4. **Détails visuels importants** : pas d'images dupliquées, pas de cartes identiques
5. Texte français destiné à la publication DOIT passer par l'agent de relecture (skill text-review-french, mistral-large-3:675b)

### Modèles d'exécution
David a demandé l'exécution avec des **modèles locaux sur son Mac** (M2 Max 32 Go) :
- Ollama local tourne sur `localhost:11434`
- Modèles disponibles localement : qwen2.5:3b, llama3.2:3b, qwen3.5:9b
- Pour le délégué (subagents) : utiliser `qwen3.5:9b` via Ollama local (0 token, 0 coût)
- Modèle principal (orchestrateur) : GLM-5.2:cloud via Ollama Cloud

### Bilinguisme FR/EN
- Bouton toggle de langue dans le header (LangToggle.astro)
- Fichiers JSON en double : `.fr.json` / `.en.json`
- Traductions d'interface dans `src/i18n/ui.json` (`{ fr: {...}, en: {...} }`)
- Détection auto de la langue navigateur (Accept-Language), FR par défaut
- Préférence stockée dans `localStorage`

### Sécurité & confidentialité
- L'API d'analyse reçoit des documents potentiellement sensibles
- HTTPS uniquement (Traefik), authentification JWT
- Suppression immédiate des fichiers après analyse (secure delete / shred)
- Pas de logging du contenu des documents
- Banner visible pendant l'analyse : "🔒 Votre document est analysé sur un serveur local et supprimé immédiatement"
- Rate limiting sur l'API

### VPS Hostinger (72.62.21.38)
- Ubuntu 24.04, n8n, Ollama (:11434)
- Traefik pour le routing : `ai-checker.srv1179315.hstgr.cloud` → `localhost:8082`
- Modèles cloud disponibles : glm-5.1/5.2, ministral-3:14b, kimi-k2.7-code, deepseek-v4-pro, qwen3.5, gemma4:31b
- Modèles locaux : qwen2.5:3b, llama3.2:3b, qwen3.5:9b

### Déploiement Vercel
- ⚠️ Pour un nouveau projet : `rm -rf .vercel && rm -rf .git` AVANT deploy si on copie un site existant
- David déploie via Vercel CLI

## Variables d'environnement requises
- `NOTION_TOKEN` — token API Notion (pour auth)
- `NOTION_USERS_DB_ID` — ID de la base Notion Utilisateurs
- `JWT_SECRET` — secret pour signer les JWT
- `OLLAMA_BASE_URL` — `http://localhost:11434` (VPS) ou `http://localhost:11434` (Mac local)
- `VPS_API_URL` — URL de l'API sur le VPS (pour le frontend)

## Prochaines étapes
1. ⬜ Trouver un nom de domaine + créer le repo GitHub
2. ⬜ Scaffolding Astro 6+ + Tailwind (Phase 1, Task 1)
3. ⬜ Base de données secteurs + modèles (Phase 2)
4. ⬜ Tableau de bord public + moteur de recherche (Phase 3)
5. ⬜ API auth Notion + analyse Ollama sur VPS (Phase 4)
6. ⬜ Déploiement Vercel + VPS (Phase 5)