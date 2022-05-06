import React from 'react';

import { useAppDispatch, useAppSelector } from '~/hooks';

import { getUserData, markAllNotificationsAsRead_, signOut_ } from '../actions';
import { NAME } from '../index';
import { SignIn } from './SignIn';
import { UserAutoUpdater } from './UserAutoUpdater';
import './UserControls.css';
import UserNotificationsMenu from './UserNotificationsMenu';
import UserMenu from './UserMenu';

export function UserControls(): React.ReactElement<'div'> {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state[NAME]);

  return (
    <div className='user-controls'>
      <UserAutoUpdater getUserData={() => dispatch(getUserData())} />

      <UserMenu
        signOut={() => dispatch(signOut_(user.signOutURL))}
        user={user}
      />

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
