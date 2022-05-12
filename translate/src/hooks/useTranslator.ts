import { useContext } from 'react';

import { Locale } from '~/context/locale';
import { useProject } from '~/core/project';
import { USER } from '~/core/user';
import { useAppSelector } from '~/hooks';

/**
 * Return true if the user has translator permission for the current project
 * and locale.
 */
export function useTranslator(): boolean {
  const { code } = useContext(Locale);
  const { slug } = useProject();
  const {
    isAuthenticated,
    managerForLocales,
    translatorForLocales,
    translatorForProjects,
  } = useAppSelector((state) => state[USER]);

  if (!isAuthenticated) {
    return false;
  }

  if (managerForLocales.includes(code)) {
    return true;
  }

  const localeProject = `${code}-${slug}`;
  if (Object.hasOwnProperty.call(translatorForProjects, localeProject)) {
    return translatorForProjects[localeProject];
  }

  return translatorForLocales.includes(code);
}
