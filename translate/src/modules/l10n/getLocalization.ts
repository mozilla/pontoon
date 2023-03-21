import { FluentBundle, FluentResource, TextTransform } from '@fluent/bundle';
import { negotiateLanguages } from '@fluent/langneg';
import { ReactLocalization } from '@fluent/react';

import { fetchL10n } from '~/api/l10n';

import { accented, bidi } from './pseudolocalization';

// List of available locales for the UI.
// Use to choose which locale files to download.
const AVAILABLE_LOCALES = ['en-US'];

/**
 * Get the UI translations for a list of locales.
 *
 * This fetches the translations for the UI for each given locale, bundles
 * those and store them to be used in showing a localized interface.
 */
export async function getLocalization(locales: readonly string[]) {
  let languages: string[];
  let bundleOptions: { transform?: TextTransform };

  // Pseudo localization shows a weirdly translated UI, based on English.
  // This is a development only tool that helps verifying that our UI
  // is properly localized.
  const searchParams = new URLSearchParams(window.location.search);
  switch (searchParams.get('pseudolocalization')) {
    case 'accented':
      languages = ['en-US'];
      bundleOptions = { transform: accented };
      break;

    case 'bidi':
      languages = ['en-US'];
      bundleOptions = { transform: bidi };
      break;

    default:
      // Setting defaultLocale to `en-US` means that it will always be the
      // last fallback locale, thus making sure the UI is always working.
      languages = negotiateLanguages(locales, AVAILABLE_LOCALES, {
        defaultLocale: 'en-US',
      });
      bundleOptions = {};
  }

  const bundles = await Promise.all(
    languages.map((locale) =>
      fetchL10n(locale).then((content) => {
        const bundle = new FluentBundle(locale, bundleOptions);
        const resource = new FluentResource(content);
        bundle.addResource(resource);
        return bundle;
      }),
    ),
  );

  return new ReactLocalization(bundles);
}
