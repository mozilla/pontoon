import { FluentBundle, FluentResource } from '@fluent/bundle';
import {
  LocalizationProvider,
  Localized,
  ReactLocalization,
} from '@fluent/react';
import React from 'react';

/*
 * Wait until `ms` milliseconds have passed.
 *
 * Source: https://stackoverflow.com/questions/951021
 */
export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/*
 * Find Localized elements by their ID.
 *
 * Source: https://github.com/mozilla/testpilot/blob/93c9ea7aa6104fbbdc21508e44d486d7ca7c77aa/frontend/test/app/util.js
 */
export function findLocalizedById(wrapper, id) {
  return wrapper.findWhere(
    (elem) => elem.type() === Localized && elem.prop('id') === id,
  );
}

/**
 * Mock the @fluent/react LocalizationProvider,
 * which is required as a wrapper for Localization.
 */
export function MockLocalizationProvider({ children, resources }) {
  const bundle = new FluentBundle('en-US');
  const resourceList = Array.isArray(resources) ? resources : [resources];

  resourceList.forEach((res) => {
    if (res) {
      const fluentResource = new FluentResource(res);
      bundle.addResource(fluentResource);
    }
  });
  const l10n = new ReactLocalization([bundle], null);

  // https://github.com/projectfluent/fluent.js/issues/411
  l10n.reportError = () => {};

  return <LocalizationProvider l10n={l10n}>{children}</LocalizationProvider>;
}
