import React, { createContext, useContext, useEffect, useState } from 'react';

import {
  abortMachineryRequests,
  fetchCaighdeanTranslation,
  fetchComposedMachinery,
  fetchGoogleTranslation,
  fetchMicrosoftTranslation,
  fetchTranslationMemory,
  MachineryTranslation,
} from '~/api/machinery';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';
import { editMessageEntry, getPlainMessage, parseEntry } from '~/utils/message';

import { EntityView, useMachineryEntry } from './EntityView';
import { Locale } from './Locale';
import { SearchData } from './SearchData';

export type MachineryTranslations = {
  fetching: boolean;
  source: string;
  translations: MachineryTranslation[];
};

const initTranslations: MachineryTranslations = {
  fetching: false,
  source: '',
  translations: [],
};

export const MachineryTranslations =
  createContext<MachineryTranslations>(initTranslations);

const sortByQuality = (
  { quality: a }: MachineryTranslation,
  { quality: b }: MachineryTranslation,
) => (!a ? 1 : !b ? -1 : a > b ? -1 : a < b ? 1 : 0);

// Formats whose entities can have multiple translatable leaves (Fluent
// attributes, MF2 selector variants). For these we request a composed
// multi-value translation in addition to the per-leaf matches. Mirrors
// `COMPOSED_FORMATS` in pontoon/machinery/views.py.
const COMPOSED_FORMATS = new Set([
  'fluent',
  'android',
  'gettext',
  'webext',
  'xcode',
  'xliff',
]);

// A composed translation is only meaningful when the entity has more than one
// translatable leaf (Fluent attributes, MF2 selector variants). For a simple
// single-field entity the composed result would just duplicate the per-leaf TM
// or MT match, so we skip the request entirely.
function hasMultipleFields(original: string, format: string): boolean {
  const entry = parseEntry(format, original);
  return !!entry && editMessageEntry(entry).length > 1;
}

export function MachineryProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const locale = useContext(Locale);
  const { isAuthenticated } = useAppSelector((state) => state[USER]);
  const { entity } = useContext(EntityView);
  const { pk } = entity;
  const entry = useMachineryEntry();
  const { query } = useContext(SearchData);

  const [fetching, setFetching] = useState(false);
  const [translations, setTranslations] = useState({
    source: '',
    translations: [] as MachineryTranslation[],
  });

  useEffect(() => {
    let cancelled = false;

    const addResults = (newTranslations: MachineryTranslation[]) => {
      if (newTranslations.length > 0) {
        setTranslations((prev) => {
          const translations = [...prev.translations];
          for (const tx of newTranslations) {
            const i = translations.findIndex(
              (t0) =>
                t0.original === tx.original &&
                t0.translation === tx.translation,
            );
            if (i === -1) {
              translations.push(tx);
            } else {
              const t0 = translations[i];
              const sources = t0.sources.concat(tx.sources);
              const quality = t0.quality ?? tx.quality;
              translations[i] = { ...t0, sources, quality };
            }
          }
          translations.sort(sortByQuality);
          return { source: prev.source, translations };
        });
      }
    };

    const plain = query || getPlainMessage(entry);

    abortMachineryRequests();
    setTranslations({ source: plain, translations: [] });

    if (plain) {
      setFetching(true);
      const promises: Promise<void>[] = [];

      // Composed multi-value translations are emitted only for entity-driven
      // navigation (not concordance search) and only for formats that can
      // have multiple translatable leaves.
      const wantsComposed =
        !query &&
        COMPOSED_FORMATS.has(entity.format) &&
        hasMultipleFields(entity.original, entity.format);

      if (!query) {
        promises.push(
          fetchTranslationMemory(plain, locale, pk).then(addResults),
        );
      }

      if (wantsComposed) {
        promises.push(
          fetchComposedMachinery(pk, locale, 'translation-memory').then(
            addResults,
          ),
        );
      }

      // Only make requests to paid services if user is authenticated
      if (isAuthenticated) {
        const root = document.getElementById('root');

        const isGoogleTranslateSupported =
          root?.dataset.isGoogleTranslateSupported === 'true';
        const isMicrosoftTranslatorSupported =
          root?.dataset.isMicrosoftTranslatorSupported === 'true';

        if (isGoogleTranslateSupported && locale.googleTranslateCode) {
          promises.push(fetchGoogleTranslation(plain, locale).then(addResults));
          if (wantsComposed) {
            promises.push(
              fetchComposedMachinery(pk, locale, 'google-translate').then(
                addResults,
              ),
            );
          }
        }

        if (isMicrosoftTranslatorSupported && locale.msTranslatorCode) {
          promises.push(
            fetchMicrosoftTranslation(plain, locale).then(addResults),
          );
          if (wantsComposed) {
            promises.push(
              fetchComposedMachinery(pk, locale, 'microsoft-translator').then(
                addResults,
              ),
            );
          }
        }
      }

      if (locale.code === 'ga-IE' && !query) {
        promises.push(fetchCaighdeanTranslation(pk).then(addResults));
      }

      Promise.allSettled(promises).then(() => {
        if (!cancelled) {
          setFetching(false);
        }
      });
    }

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, locale, pk, query || entry]);

  return (
    <MachineryTranslations.Provider value={{ ...translations, fetching }}>
      {children}
    </MachineryTranslations.Provider>
  );
}
