// Recommender — matching sensibilité × modèle → recommandation
import recommendations from '../data/recommendations.json';
import modelsFr from '../data/models.fr.json';
import modelsEn from '../data/models.en.json';

export type SensitivityLevel = 'low' | 'medium' | 'high' | 'critical';
export type Lang = 'fr' | 'en';

interface Model {
  id: string;
  label: string;
  editor: string;
  jurisdiction: string;
  jurisdiction_flag: string;
  data_retention: string;
  training_on_data: boolean;
  api_retention: string;
  risk_level: string;
  risk_description: string;
  gdpr_compliant: string;
  notes: string;
  safe_for_levels: string[];
}

interface RecommendationResult {
  recommended: Model[];
  caution: Model[];
  forbidden: Model[];
  local_only: boolean;
  best_match: Model | null;
  best_match_reason: string;
}

export function getRecommendations(sensitivity: SensitivityLevel, lang: Lang): RecommendationResult {
  const matrix = recommendations.matrix[sensitivity];
  const models = lang === 'fr' ? modelsFr.models : modelsEn.models;

  const findById = (id: string) => models.find((m: Model) => m.id === id);

  const recommended = (matrix.recommended || []).map(findById).filter(Boolean) as Model[];
  const caution = (matrix.caution || []).map(findById).filter(Boolean) as Model[];
  const forbidden = (matrix.forbidden || []).map(findById).filter(Boolean) as Model[];

  // Best match: prefer local models for critical, EU models for high, best available otherwise
  let best_match: Model | null = null;
  let best_match_reason = '';

  if (sensitivity === 'critical') {
    best_match = recommended.find(m => m.jurisdiction === 'LOCAL') || recommended[0] || null;
    best_match_reason = lang === 'fr'
      ? 'Document critique : seul un modèle local garantit que vos données ne quittent jamais votre machine.'
      : 'Critical document: only a local model guarantees your data never leaves your machine.';
  } else if (sensitivity === 'high') {
    best_match = recommended.find(m => m.jurisdiction === 'FR/EU') || recommended.find(m => m.jurisdiction === 'LOCAL') || recommended[0] || null;
    best_match_reason = lang === 'fr'
      ? 'Document sensible : privilégiez un modèle hébergé en UE ou local pour minimiser les risques.'
      : 'Sensitive document: prefer an EU-hosted or local model to minimize risks.';
  } else if (sensitivity === 'medium') {
    best_match = recommended.find(m => m.jurisdiction === 'FR/EU' && !m.training_on_data) || recommended[0] || null;
    best_match_reason = lang === 'fr'
      ? 'Données modérées : un modèle européen sans entraînement sur vos données est recommandé.'
      : 'Moderate data: a European model without training on your data is recommended.';
  } else {
    best_match = recommended.find(m => m.jurisdiction === 'FR/EU') || recommended[0] || null;
    best_match_reason = lang === 'fr'
      ? 'Faible sensibilité : tous les modèles sont utilisables, préférez un modèle EU par défaut.'
      : 'Low sensitivity: all models are usable, prefer an EU model by default.';
  }

  return {
    recommended,
    caution,
    forbidden,
    local_only: matrix.local_only,
    best_match,
    best_match_reason,
  };
}