import React, { useEffect, useState } from 'react';
import { LocalizationProvider, ReactLocalization } from '@fluent/react';

import { getLocalization } from '../getLocalization';

type Props = {
  children: React.ReactNode;
};

/**
 * Localization provider for this application.
 *
 * This Component is in charge of fetching translations for the application's
 * context and providing them to the underlying Localized elements.
 *
 * Until the translations are received, `localization.parseMarkup === null` is true.
 */
export function AppLocalizationProvider({
  children,
}: Props): React.ReactElement {
  const [localization, setLocalization] = useState<ReactLocalization>(
    () => new ReactLocalization([], null),
  );

  useEffect(() => {
    const lang = document.documentElement?.lang;
    const locales = lang ? [lang] : navigator.languages;
    getLocalization(locales).then(setLocalization);
  }, []);

  return (
    <LocalizationProvider l10n={localization}>{children}</LocalizationProvider>
  );
}
