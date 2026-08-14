import { useContext } from 'react';

import type { Entity } from '~/api/entity';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { useProject } from '~/modules/project';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';

/**
 * Return true if the user has translator permission for the current project
 * and locale.
 *
 * @param entity Used in the All Projects view to check the permission.
 */
export function useTranslator(entity?: Entity): boolean {
  const { code } = useContext(Locale);
  const { slug } = useProject();
  const selected = useContext(EntityView)?.entity;
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

  const projectSlug =
    slug === 'all-projects' ? (entity ?? selected)?.project?.slug : slug;

  const localeProject = `${code}-${projectSlug}`;
  if (Object.hasOwnProperty.call(translatorForProjects, localeProject)) {
    return translatorForProjects[localeProject];
  }

  return canTranslateLocales.includes(code);
}
