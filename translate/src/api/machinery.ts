import type { Locale } from '~/context/Locale';

import { GET } from './utils/base';

/*
 * Translation that comes from a machine (Machine Translation,
 * Translation Memory... ).
 */
export type SourceType =
  | 'concordance-search'
  | 'translation-memory'
  | 'google-translate'
  | 'microsoft-translator'
  | 'systran-translate'
  | 'microsoft-terminology'
  | 'caighdean';

export type MachineryTranslation = {
  sources: SourceType[];
  itemCount?: number;
  original: string;
  translation: string;
  quality?: number;
  projectNames?: Array<string | null>;
};

type ConcordanceTranslations = {
  results: Array<MachineryTranslation>;
  hasMore: boolean;
};

let abortController = new AbortController();

export function abortMachineryRequests() {
  abortController.abort();
  abortController = new AbortController();
}

function GET_(url: string, params: Record<string, string>) {
  const search = new URLSearchParams(params);
  return GET(url, search, { signal: abortController.signal });
}

/**
 * Return results from Concordance search.
 *
 * Note! Not under common machinery abort controller
 */
export async function fetchConcordanceResults(
  source: string,
  locale: Locale,
  page?: number,
): Promise<ConcordanceTranslations> {
  const url = '/concordance-search/';
  const params = new URLSearchParams({
    text: source,
    locale: locale.code,
    page: String(page || 1),
  });

  const { results, has_next } = (await GET(url, params, {
    singleton: true,
  })) as {
    results: Array<{
      source: string;
      target: string;
      project_names: string[];
    }>;
    has_next: boolean;
  };

  return Array.isArray(results)
    ? {
        results: results.map((item) => ({
          sources: ['concordance-search'],
          original: item.source,
          translation: item.target,
          projectNames: item.project_names,
        })),
        hasMore: has_next,
      }
    : { results: [], hasMore: false };
}

/**
 * Return translations from Pontoon's memory.
 */
export async function fetchTranslationMemory(
  source: string,
  locale: Locale,
  pk: number | null | undefined,
): Promise<MachineryTranslation[]> {
  const url = '/translation-memory/';
  let params: Record<string, string> = {
    text: source,
    locale: locale.code,
  };

  if (pk) {
    params[pk] = String(pk);
  }

  const results = (await GET_(url, params)) as Array<{
    count: number;
    source: string;
    target: string;
    quality: number;
  }>;

  return Array.isArray(results)
    ? results.map((item) => ({
        sources: ['translation-memory'],
        itemCount: item.count,
        original: item.source,
        translation: item.target,
        quality: Math.floor(item.quality),
      }))
    : [];
}

/**
 * Return translation by Google Translate.
 */
export async function fetchGoogleTranslation(
  original: string,
  locale: Locale,
): Promise<MachineryTranslation[]> {
  const url = '/google-translate/';
  const params = {
    text: original,
    locale: locale.googleTranslateCode,
  };

  const { translation } = (await GET_(url, params)) as {
    translation: string;
  };

  return translation
    ? [{ sources: ['google-translate'], original, translation }]
    : [];
}

/**
 * Return translation by Microsoft Translator.
 */
export async function fetchMicrosoftTranslation(
  original: string,
  locale: Locale,
): Promise<MachineryTranslation[]> {
  const url = '/microsoft-translator/';
  const params = {
    text: original,
    locale: locale.msTranslatorCode,
  };

  const { translation } = (await GET_(url, params)) as {
    translation: string;
  };

  return translation
    ? [{ sources: ['microsoft-translator'], original, translation }]
    : [];
}

/**
 * Return translations by SYSTRAN.
 */
export async function fetchSystranTranslation(
  original: string,
  locale: Locale,
): Promise<MachineryTranslation[]> {
  const url = '/systran-translate/';
  const params = {
    text: original,
    locale: locale.systranTranslateCode,
  };

  const { translation } = (await GET_(url, params)) as {
    translation: string;
  };

  return translation
    ? [{ sources: ['systran-translate'], original, translation }]
    : [];
}

/**
 * Return translations from Microsoft Terminology.
 */
export async function fetchMicrosoftTerminology(
  source: string,
  locale: Locale,
): Promise<MachineryTranslation[]> {
  const url = '/microsoft-terminology/';
  const params = {
    text: source,
    locale: locale.msTerminologyCode,
  };

  const { translations } = (await GET_(url, params)) as {
    translations: Array<{ source: string; target: string }>;
  };

  return translations
    ? translations.map((item) => ({
        sources: ['microsoft-terminology'],
        original: item.source,
        translation: item.target,
      }))
    : [];
}

/**
 * Return translation by Caighdean Machine Translation.
 *
 * Works only for the `ga-IE` locale.
 */
export async function fetchCaighdeanTranslation(
  pk: number,
): Promise<MachineryTranslation[]> {
  const url = '/caighdean/';
  const params = { id: String(pk) };

  const { original, translation } = (await GET_(url, params)) as {
    original: string;
    translation: string;
  };

  return translation ? [{ sources: ['caighdean'], original, translation }] : [];
}
