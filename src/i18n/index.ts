// i18n helper — bilingual FR/EN support
import ui from './ui.json';

export type Lang = 'fr' | 'en';

export function getLangFromUrl(url: URL): Lang {
  const [, lang] = url.pathname.split('/');
  if (lang === 'en' || lang === 'fr') return lang;
  // Default to FR
  return 'fr';
}

export function getLangFromCookie(cookieHeader: string | null): Lang {
  if (!cookieHeader) return 'fr';
  const match = cookieHeader.match(/preferred_lang=(fr|en)/);
  return match ? (match[1] as Lang) : 'fr';
}

export function t(lang: Lang, path: string): string {
  const keys = path.split('.');
  let value: any = ui[lang];
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      return path; // fallback: return the key path
    }
  }
  return typeof value === 'string' ? value : path;
}

export function tObj(lang: Lang) {
  return ui[lang] as any;
}