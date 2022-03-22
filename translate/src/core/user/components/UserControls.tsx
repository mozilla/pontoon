import React from 'react';
import { connect } from 'react-redux';

import type { Entity } from '~/core/api';
import { getSelectedEntity } from '~/core/entities/selectors';
import type { NavigationParams } from '~/core/navigation';
import { getNavigationParams } from '~/core/navigation/selectors';
import type { UserState } from '~/core/user';
import { AppDispatch, RootState } from '~/store';

import {
  get as getUserData,
  markAllNotificationsAsRead,
  signOut,
} from '../actions';
import { NAME } from '../index';
import SignIn from './SignIn';
import UserAutoUpdater from './UserAutoUpdater';
import UserNotificationsMenu from './UserNotificationsMenu';
import UserMenu from './UserMenu';

import './UserControls.css';

type Props = {
  parameters: NavigationParams;
  selectedEntity?: Entity;
  user: UserState;
};

type InternalProps = Props & {
  dispatch: AppDispatch;
};

export const UserControlsBase = ({
  dispatch,
  parameters,
  selectedEntity,
  user,
}: InternalProps): React.ReactElement<'div'> => (
  <div className='user-controls'>
    <UserAutoUpdater getUserData={() => dispatch(getUserData())} />

    <UserMenu
      isReadOnly={selectedEntity ? selectedEntity.readonly : true}
      parameters={parameters}
      signOut={() => dispatch(signOut(user.signOutURL))}
      user={user}
    />

    <UserNotificationsMenu
      markAllNotificationsAsRead={() => dispatch(markAllNotificationsAsRead())}
      user={user}
    />

    {user.isAuthenticated ? null : <SignIn url={user.signInURL} />}
  </div>
);

const mapStateToProps = (state: RootState): Props => {
  return {
    parameters: getNavigationParams(state),
    selectedEntity: getSelectedEntity(state),
    user: state[NAME],
  };
};

export default connect(mapStateToProps)(UserControlsBase) as any;
