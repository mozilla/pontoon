import { useContext } from 'react';

import { Locale } from '../../src/context/Locale';
import { useProject } from '../../src/modules/project';
import { USER } from '../../src/modules/user';
import { useAppSelector } from '../../src/hooks';

/**
 * Return true if the user has translator permission for the current project
 * and locale.
 */
export function useTranslator(): boolean {
  const { code } = useContext(Locale);
  const { slug } = useProject();
  const {
    isAuthenticated,
    canManageLocales,
    canTranslateLocales,
    translatorForProjects,
  } = useAppSelector((state) => state[USER]);

  if (!isAuthenticated) {
    return false;
  }

  if (canManageLocales.includes(code)) {
    return true;
  }

  const localeProject = `${code}-${slug}`;
  if (Object.hasOwnProperty.call(translatorForProjects, localeProject)) {
    return translatorForProjects[localeProject];
  }

  return canTranslateLocales.includes(code);
}
