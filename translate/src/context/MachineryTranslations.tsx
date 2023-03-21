import React, { createContext, useContext, useEffect, useState } from 'react';

import {
  abortMachineryRequests,
  fetchCaighdeanTranslation,
  fetchGoogleTranslation,
  fetchMicrosoftTerminology,
  fetchMicrosoftTranslation,
  fetchSystranTranslation,
  fetchTranslationMemory,
  MachineryTranslation,
} from '~/api/machinery';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';
import { getPlainMessage } from '~/utils/message';

import { EntityView } from './EntityView';
import { Locale } from './Locale';
import { SearchData } from './SearchData';

export type MachineryTranslations = {
  source: string;
  translations: MachineryTranslation[];
};

const initTranslations: MachineryTranslations = {
  source: '',
  translations: [],
};

export const MachineryTranslations =
  createContext<MachineryTranslations>(initTranslations);

const sortByQuality = (
  { quality: a }: MachineryTranslation,
  { quality: b }: MachineryTranslation,
) => (!a ? 1 : !b ? -1 : a > b ? -1 : a < b ? 1 : 0);

export function MachineryProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const locale = useContext(Locale);
  const { isAuthenticated } = useAppSelector((state) => state[USER]);
  const { entity } = useContext(EntityView);
  const { query } = useContext(SearchData);

  let source: string;
  let pk: number | null;
  let format: string;
  if (query) {
    source = query;
    pk = null;
    format = '';
  } else {
    source = entity.machinery_original;
    pk = entity.pk;
    format = entity.format;
  }

  const [translations, setTranslations] =
    useState<MachineryTranslations>(initTranslations);

  useEffect(() => {
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

    const plain = getPlainMessage(source, format);

    abortMachineryRequests();
    setTranslations({ source: plain, translations: [] });

    if (plain) {
      if (pk) {
        fetchTranslationMemory(plain, locale, pk).then(addResults);
      }

      // Only make requests to paid services if user is authenticated
      if (isAuthenticated) {
        if (locale.googleTranslateCode) {
          fetchGoogleTranslation(plain, locale).then(addResults);
        }

        if (locale.msTranslatorCode) {
          fetchMicrosoftTranslation(plain, locale).then(addResults);
        }

        if (locale.systranTranslateCode) {
          fetchSystranTranslation(plain, locale).then(addResults);
        }
      }

      if (locale.msTerminologyCode) {
        fetchMicrosoftTerminology(plain, locale).then(addResults);
      }

      if (locale.code === 'ga-IE' && pk) {
        fetchCaighdeanTranslation(pk).then(addResults);
      }
    }
  }, [isAuthenticated, locale, source, pk, format]);

  return (
    <MachineryTranslations.Provider value={translations}>
      {children}
    </MachineryTranslations.Provider>
  );
}
