import React from 'react';

import { useAppDispatch, useAppSelector } from '~/hooks';

import { getUserData, markAllNotificationsAsRead_ } from '../actions';
import { USER } from '../reducer';
import { SignIn } from './SignIn';
import { UserAutoUpdater } from './UserAutoUpdater';
import './UserControls.css';
import { UserNotificationsMenu } from './UserNotificationsMenu';
import { UserMenu } from './UserMenu';

import { saveTheme } from '../actions';

export function UserControls(): React.ReactElement<'div'> {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state[USER]);

  const handleThemeChange = (newTheme: string) => {
    if (user.username) {
      dispatch(saveTheme(newTheme, user.username));
    }
  };

  return (
    <div className='user-controls'>
      <UserAutoUpdater getUserData={() => dispatch(getUserData())} />

      <UserMenu user={user} onThemeChange={handleThemeChange} />

      <UserNotificationsMenu
        markAllNotificationsAsRead={() =>
          dispatch(markAllNotificationsAsRead_())
        }
        user={user}
      />

      {user.isAuthenticated ? null : <SignIn url={user.signInURL} />}
    </div>
  );
}
