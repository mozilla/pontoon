import { isSelectMessage, messagesEqual, type Message } from '@mozilla/l10n';
import React, { createContext, useContext, useEffect, useState } from 'react';

import {
  abortMachineryRequests,
  ComposedMachineryTranslation,
  fetchCaighdeanTranslation,
  fetchComposedMachinery,
  fetchGoogleTranslation,
  fetchMicrosoftTranslation,
  fetchTranslationMemory,
  MachineryTranslation,
} from '~/api/machinery';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';
import { findPluralSelectors, getPlainMessage } from '~/utils/message';

import { EntityView, useMachineryEntry } from './EntityView';
import { Locale } from './Locale';
import { SearchData } from './SearchData';

export type MachineryTranslations = {
  fetching: boolean;
  source: string;
  // Composed multi-value suggestions, rendered above the per-leaf matches.
  composed: ComposedMachineryTranslation[];
  translations: MachineryTranslation[];
};

const initTranslations: MachineryTranslations = {
  fetching: false,
  source: '',
  composed: [],
  translations: [],
};

export const MachineryTranslations =
  createContext<MachineryTranslations>(initTranslations);

// Sort by descending quality; entries without a quality score sort last.
const sortByQuality = (a: { quality?: number }, b: { quality?: number }) => {
  const { quality: qa } = a;
  const { quality: qb } = b;
  return !qa ? 1 : !qb ? -1 : qa > qb ? -1 : qa < qb ? 1 : 0;
};

// A composed translation only adds something when the entity has more than one
// translatable pattern in the target; otherwise it just duplicates the per-leaf
// TM or MT match, so we skip the request.
function hasMultipleFields(
  value: Message,
  properties: Record<string, Message> | undefined,
  pluralCategories: number,
): boolean {
  let leaves = 0;
  for (const msg of [value, ...Object.values(properties ?? {})]) {
    if (!msg) {
      continue;
    }
    if (isSelectMessage(msg)) {
      // Plural selectors expand to the locale's CLDR categories the way
      // walk_entity() does; any other selector is multi-pattern as soon as the
      // message declares more than one variant.
      const plurals = findPluralSelectors(msg);
      if (
        plurals.size === msg.sel.length
          ? pluralCategories > 1
          : msg.alt.length > 1
      ) {
        return true;
      }
      leaves += 1;
    } else {
      // An empty pattern — e.g. the value of an attribute-only Fluent message
      // — has nothing to translate and is not a leaf.
      const pattern = Array.isArray(msg) ? msg : msg.msg;
      if (pattern && pattern.length > 0) {
        leaves += 1;
      }
    }
    if (leaves > 1) {
      return true;
    }
  }
  return false;
}

/** Composed suggestions are identified by their `(value, properties)` model. */
function composedEquals(
  a: ComposedMachineryTranslation,
  b: ComposedMachineryTranslation,
): boolean {
  if (!messagesEqual(a.value, b.value)) {
    return false;
  }
  const ap = a.properties ?? {};
  const bp = b.properties ?? {};
  const keys = Object.keys(ap);
  return (
    keys.length === Object.keys(bp).length &&
    keys.every((key) => key in bp && messagesEqual(ap[key], bp[key]))
  );
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
    composed: [] as ComposedMachineryTranslation[],
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
          return { ...prev, translations };
        });
      }
    };

    // The TM-only and MT-backed requests can yield the same composition, in
    // which case we merge their source badges rather than list it twice.
    const addComposed = (newComposed: ComposedMachineryTranslation[]) => {
      if (newComposed.length > 0) {
        setTranslations((prev) => {
          const composed = [...prev.composed];
          for (const tx of newComposed) {
            const i = composed.findIndex((t0) => composedEquals(t0, tx));
            if (i === -1) {
              composed.push(tx);
            } else {
              const t0 = composed[i];
              const sources = t0.sources.concat(tx.sources);
              const quality = t0.quality ?? tx.quality;
              composed[i] = { ...t0, sources, quality };
            }
          }
          composed.sort(sortByQuality);
          return { ...prev, composed };
        });
      }
    };

    const plain = query || getPlainMessage(entry);

    abortMachineryRequests();
    setTranslations({ source: plain, composed: [], translations: [] });

    if (plain) {
      setFetching(true);
      const promises: Promise<void>[] = [];

      const wantsComposed =
        !query &&
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
            addComposed,
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
                addComposed,
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
                addComposed,
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
