import React from 'react';
import { connect } from 'react-redux';

import { AppDispatch, RootState } from '~/store';

import {
  get as getUserData,
  markAllNotificationsAsRead,
  signOut,
} from '../actions';
import { NAME, UserState } from '../index';
import { SignIn } from './SignIn';
import { UserAutoUpdater } from './UserAutoUpdater';
import UserNotificationsMenu from './UserNotificationsMenu';
import UserMenu from './UserMenu';

import './UserControls.css';

type Props = {
  user: UserState;
};

type InternalProps = Props & {
  dispatch: AppDispatch;
};

export const UserControlsBase = ({
  dispatch,
  user,
}: InternalProps): React.ReactElement<'div'> => (
  <div className='user-controls'>
    <UserAutoUpdater getUserData={() => dispatch(getUserData())} />

    <UserMenu signOut={() => dispatch(signOut(user.signOutURL))} user={user} />

    <UserNotificationsMenu
      markAllNotificationsAsRead={() => dispatch(markAllNotificationsAsRead())}
      user={user}
    />

    {user.isAuthenticated ? null : <SignIn url={user.signInURL} />}
  </div>
);

const mapStateToProps = (state: RootState): Props => ({ user: state[NAME] });

export default connect(mapStateToProps)(UserControlsBase) as any;
