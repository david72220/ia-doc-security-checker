# Informations du Projet

## Nom du Projet
IA Doc Security Checker

## Date de création/mise à jour
01/07/2026 17:07:57

## Description
Outil web permettant de vérifier le niveau de sécurité des documents professionnels avant de les utiliser avec des modèles d'IA. Classification par secteur (comptabilité, commercial, juridique, RH, etc.) avec recommandations de modèles IA adaptés selon la sensibilité des données.

## Stack Technique
- **Framework**: Astro 6+ (static site avec SSR pour API routes)
- **Styling**: Tailwind CSS
- **Déploiement**: Vercel (serverless functions)
- **i18n**: Bilingue FR/EN
- **Backend**: FastAPI (non déployé - prévu pour VPS Hostinger)

## Structure du projet
```
src/
├── pages/
│   ├── [lang]/
│   │   ├── index.astro        # Page d'accueil avec sélection type entreprise
│   │   ├── tableau.astro      # Tableau de bord avec secteurs/documents
│   │   ├── analyse.astro      # Upload et analyse de documents
│   │   ├── resultat.astro     # Résultats avec recommandations
│   │   └── a-propos.astro     # Page À propos
│   └── api/
│       └── health.ts          # Health check endpoint
├── layouts/
│   └── Layout.astro           # Layout principal avec navigation
├── data/
│   ├── sectors.fr.json        # Secteurs et documents (FR) - 15 secteurs, 80+ docs
│   ├── sectors.en.json        # Secteurs et documents (EN)
│   ├── models.fr.json         # Modèles IA avec juridictions (FR)
│   ├── models.en.json         # Modèles IA (EN)
│   └── recommendations.json   # Matrice de recommandations par sensibilité
├── i18n/
│   ├── index.ts               # Utilitaires i18n
│   └── ui.json                # Traductions FR/EN
└── styles/
    └── global.css             # Styles globaux Tailwind
```

## Fichiers importants

- `astro.config.mjs` - Configuration Astro avec adapter Vercel
- `src/data/sectors.fr.json` - Base de données des secteurs/documents
- `src/data/models.fr.json` - Base de données des modèles IA
- `src/data/recommendations.json` - Logique de recommandation par sensibilité
- `src/i18n/ui.json` - Toutes les traductions FR/EN

## URLs de production

- **Site**: https://ia-doc-security.vercel.app
- **Health API**: https://ia-doc-security.vercel.app/api/health
- **GitHub**: https://github.com/david72220/ia-doc-security-checker

## Informations Git

### Derniers commits
```
8e17ecc chore: remove all login/auth references from UI and translations
03d5ed9 chore: remove 'Connexion' from nav, replace login links with analyze
f4c931b chore: remove Notion auth - public access only, clean up API routes
141d6f7 debug: add test-notion endpoint
3774e03 debug: add detailed error info for Notion API
```

### Branche actuelle
```
main
```

### Statut (fichiers modifiés)
```
 M Claude.md
?? Claude.md.backup.1782918477
```

## Variables d'environnement

Fichier `.env` (non commité) :
- `NOTION_TOKEN` - Token API Notion (non utilisé actuellement)
- `NOTION_USERS_DB_ID` - ID de la database Notion (non utilisé actuellement)

## Déploiement Vercel

```bash
# Build
npm run build

# Déploiement production
vercel --prod --yes
```

## Architecture des données

### Niveaux de sensibilité
- `low` - Documents publics (ex: devis standard)
- `medium` - Données commerciales non sensibles
- `high` - Données personnelles RGPD, finances détaillées
- `critical` - Secrets industriels, santé, credentials

### Juridictions des modèles IA
- `LOCAL` - Modèles locaux (Ollama, LM Studio)
- `FR/EU` - Mistral, OVHcloud, LightOn
- `US` - OpenAI, Anthropic, Google
- `CN` - Modèles chinois
- `OTHER` - Autres juridictions

### Critères de recommandation
1. Sensibilité du document
2. Juridiction du fournisseur IA
3. Politique de rétention des données
4. Entraînement sur les données utilisateur

## Pitfall: NFD/NFC encoding

Le dossier du projet a été créé via macOS Finder (NFD encoding). Les outils Hermes écrivent en NFC. Toujours utiliser le terminal pour les opérations de fichiers :

```bash
# Correct
cd "/Users/davidollivier/Documents/Antigravity/Outil securité documents par l'IA"
~/.hermes/scripts/eclaude.sh

# Incorrect (peut créer un phantom directory NFC)
write_file path="/Users/davidollivier/Documents/Antigravity/Outil securite documents par l'IA/..."
```

## Prochaines étapes (TODO)

- [ ] Déployer backend FastAPI sur VPS Hostinger (72.62.21.38)
- [ ] Implémenter l'analyse réelle de documents avec modèle local
- [ ] Ajouter page de recherche par mot-clé
- [ ] Intégrer base Notion pour contenu dynamique