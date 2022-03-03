import { createSelector } from 'reselect';

import { NAME as LOCALE_NAME } from '~/core/locale';
import { NAME as PROJECT_NAME } from '~/core/project';

import { NAME } from '.';

import type { RootState } from '../../store';

const userSelector = (state: RootState) => state[NAME];
const localeSelector = (state: RootState) => state[LOCALE_NAME];
const projectSelector = (state: RootState) => state[PROJECT_NAME];

export function _isTranslator(
  user: ReturnType<typeof userSelector>,
  locale: ReturnType<typeof localeSelector>,
  project: ReturnType<typeof projectSelector>,
): boolean {
  const localeProject = locale.code + '-' + project.slug;

  if (!user.isAuthenticated) {
    return false;
  }

  if (user.managerForLocales.indexOf(locale.code) !== -1) {
    return true;
  }

  if (Object.hasOwnProperty.call(user.translatorForProjects, localeProject)) {
    return user.translatorForProjects[localeProject];
  }

  return user.translatorForLocales.indexOf(locale.code) !== -1;
}

/**
 * Return true if the user has translator permission for the current project
 * and locale.
 */
export const isTranslator = createSelector(
  userSelector,
  localeSelector,
  projectSelector,
  _isTranslator,
);

export default {
  isTranslator,
};
