import { useContext } from 'react';

import { Locale } from '~/context/Locale';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';

/**
 * Return the user's status within the given locale, to display on the user banner
 */
export function useLocaleRole(): Array<string> {
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

  if (isAdmin) {
    return ['ADMIN', 'Admin'];
  }

  if (Object.hasOwnProperty.call(managerForLocales, code)) {
    return ['MNGR', 'Manger'];
  }

  if (Object.hasOwnProperty.call(translatorForLocales, code)) {
    return ['TRNSL', 'Translator'];
  }

  const dateJoinedObj = new Date(dateJoined);
  let newUserDate = dateJoinedObj;
  newUserDate.setMonth(dateJoinedObj.getMonth() - 3);
  if (dateJoinedObj < newUserDate) {
    return ['NEW USER', 'New User'];
  }

  return ['', ''];
}
