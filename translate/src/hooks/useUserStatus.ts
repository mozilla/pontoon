import { useContext } from 'react';

import { Locale } from '~/context/Locale';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';

/**
 * Return the user's status within the given locale, to display on the user banner
 */
export function useUserStatus(): Array<string> {
  const { code } = useContext(Locale);
  const {
    isAuthenticated,
    isAdmin,
    managerForLocales,
    translatorForLocales,
    dateJoined,
  } = useAppSelector((state) => state[USER]);

  if (!isAuthenticated) {
    return ['', ''];
  }

  if (managerForLocales.includes(code)) {
    return ['MNGR', 'Manager'];
  }

  if (translatorForLocales.includes(code)) {
    return ['TRNSL', 'Translator'];
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
