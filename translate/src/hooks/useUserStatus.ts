import { useContext } from 'react';

import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';

/**
 * Return the user's status within the given locale, to display on the user banner
 */
export function useUserStatus(): Array<string> {
  const { code } = useContext(Locale);
  const { project } = useContext(Location);
  const {
    isAuthenticated,
    isAdmin,
    canManageLocales,
    canTranslateLocales,
    pmForProjects,
    dateJoined,
  } = useAppSelector((state) => state[USER]);

  if (!isAuthenticated) {
    return ['', ''];
  }

  // Check status within the locale before checking for Project Manager or Admin
  if (canManageLocales.includes(code)) {
    return ['MNGR', 'Team Manager'];
  }

  if (canTranslateLocales.includes(code)) {
    return ['TRNSL', 'Translator'];
  }

  if (pmForProjects.includes(project)) {
    return ['PM', 'Project Manager'];
  }

  if (isAdmin) {
    return ['ADMIN', 'Admin'];
  }

  const dateJoinedObj = new Date(dateJoined);
  let threeMonthsAgo = new Date();
  threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
  if (dateJoinedObj > threeMonthsAgo) {
    return ['NEW', 'New User'];
  }

  return ['', ''];
}
