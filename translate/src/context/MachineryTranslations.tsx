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
import {
  findPluralSelectors,
  getPlainMessage,
  specialFormats,
} from '~/utils/message';

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

// Number of *target* patterns a message contributes: zero for an empty value
// (a Fluent value is empty when the message only has attributes), one for a
// plain pattern, and one per selector variant for a select message — with
// plural-selector dimensions expanded to the target locale's CLDR plural
// categories. This mirrors the plural expansion the backend's walk_entity()
// performs, so an en-US `*[other]`-only source still counts as multi-pattern
// for locales like Slovenian (one/two/few/other).
function patternCount(
  msg: Message | null | undefined,
  pluralCategories: number,
): number {
  if (!msg) {
    return 0;
  }
  if (!isSelectMessage(msg)) {
    // A pattern with no elements — e.g. the value of a Fluent message that
    // only has attributes — has nothing to translate and is not a leaf. This
    // mirrors the backend's `_pattern_count`, so an attribute-only entity is
    // not treated as multi-pattern (which would compose a redundant suggestion
    // duplicating the single per-leaf match).
    const pattern = Array.isArray(msg) ? msg : msg.msg;
    return pattern && pattern.length > 0 ? 1 : 0;
  }
  const plurals = findPluralSelectors(msg);
  let count = 1;
  for (let i = 0; i < msg.sel.length; ++i) {
    if (plurals.has(i)) {
      count *= Math.max(1, pluralCategories);
    } else {
      // Non-plural selector (e.g. a gender): keep its distinct source keys.
      const keys = new Set(
        msg.alt.map((v) => {
          const key = v.keys[i];
          return typeof key === 'string' ? key : '*';
        }),
      );
      count *= keys.size || 1;
    }
  }
  return count;
}

// A composed translation is only meaningful when the entity has more than one
// translatable leaf in the target (Fluent attributes, MF2 selector variants).
// For a single-field target the composed result would just duplicate the
// per-leaf TM or MT match, so we skip the request entirely.
function hasMultipleFields(
  value: Message,
  properties: Record<string, Message> | undefined,
  pluralCategories: number,
): boolean {
  let count = patternCount(value, pluralCategories);
  for (const prop of Object.values(properties ?? {})) {
    count += patternCount(prop, pluralCategories);
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
        hasMultipleFields(
          entity.value,
          entity.properties,
          locale.cldrPlurals.length,
        );

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
