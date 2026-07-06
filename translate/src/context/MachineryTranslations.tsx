import { isSelectMessage, type Message } from '@mozilla/l10n';
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
import { getPlainMessage, specialFormats } from '~/utils/message';

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

// Composed multi-value suggestions always sort to the top, ahead of the
// per-leaf matches; within each group we sort by descending quality.
const sortByQuality = (a: MachineryTranslation, b: MachineryTranslation) => {
  if (a.composed !== b.composed) {
    return a.composed ? -1 : 1;
  }
  const { quality: qa } = a;
  const { quality: qb } = b;
  return !qa ? 1 : !qb ? -1 : qa > qb ? -1 : qa < qb ? 1 : 0;
};

// Translatable leaves in a message: one per selector variant, or a single
// pattern otherwise. Mirrors `_pattern_count` in machinery/views.py.
function patternCount(msg: Message | null | undefined): number {
  if (!msg) {
    return 0;
  }
  return isSelectMessage(msg) ? msg.alt.length : 1;
}

// A composed translation is only meaningful when the entity has more than one
// translatable leaf (Fluent attributes, MF2 selector variants). For a simple
// single-field entity the composed result would just duplicate the per-leaf TM
// or MT match, so we skip the request entirely.
//
// This counts the entity's *source* leaves as a heuristic: it can undercount a
// source whose selector (e.g. a plural) has fewer categories than the target
// locale needs, where the target would require multiple patterns even though
// the source has one. We accept that gap rather than resolving target plurals
// here — same limitation as machinery/views.py.
function hasMultipleFields(
  value: Message,
  properties: Record<string, Message> | undefined,
): boolean {
  let count = patternCount(value);
  for (const prop of Object.values(properties ?? {})) {
    count += patternCount(prop);
  }
  return count > 1;
}

export function MachineryProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const locale = useContext(Locale);
  const { isAuthenticated } = useAppSelector((state) => state[USER]);
  const { entity } = useContext(EntityView);
  const { pk, format } = entity;
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
        specialFormats.has(format) &&
        hasMultipleFields(entity.value, entity.properties);

      if (!query) {
        promises.push(
          fetchTranslationMemory(plain, locale, pk).then(addResults),
        );
      }

      if (wantsComposed) {
        promises.push(
          fetchComposedMachinery(pk!, locale, 'translation-memory').then(
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
              fetchComposedMachinery(pk!, locale, 'google-translate').then(
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
              fetchComposedMachinery(pk!, locale, 'microsoft-translator').then(
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
