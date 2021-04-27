/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './UserControls.css';

import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import * as user from 'core/user';

import SignIn from './SignIn';
import UserAutoUpdater from './UserAutoUpdater';
import UserNotificationsMenu from './UserNotificationsMenu';
import UserMenu from './UserMenu';
import { actions, NAME } from '..';

import type { Entity } from 'core/api';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';

type Props = {|
    isTranslator: boolean,
    parameters: NavigationParams,
    selectedEntity: Entity,
    user: UserState,
|};

type InternalProps = {
    ...Props,
    dispatch: Function,
};

export class UserControlsBase extends React.Component<InternalProps> {
    getUserData: () => void = () => {
        this.props.dispatch(actions.get());
    };

    logUxAction: (
        action_type: string,
        experiment: ?string,
        data: ?any,
    ) => void = (action_type, experiment, data) => {
        this.props.dispatch(actions.logUxAction(action_type, experiment, data));
    };

    markAllNotificationsAsRead: () => void = () => {
        this.props.dispatch(actions.markAllNotificationsAsRead());
    };

    signUserOut: () => void = () => {
        const { user } = this.props;
        this.props.dispatch(actions.signOut(user.signOutURL));
    };

    render(): React.Element<'div'> {
        const { isTranslator, parameters, user, selectedEntity } = this.props;

        const isReadOnly = selectedEntity ? selectedEntity.readonly : true;

        return (
            <div className='user-controls'>
                <UserAutoUpdater getUserData={this.getUserData} />

                <UserMenu
                    isReadOnly={isReadOnly}
                    isTranslator={isTranslator}
                    parameters={parameters}
                    signOut={this.signUserOut}
                    user={user}
                />

                <UserNotificationsMenu
                    logUxAction={this.logUxAction}
                    markAllNotificationsAsRead={this.markAllNotificationsAsRead}
                    user={user}
                />

                {user.isAuthenticated ? null : <SignIn url={user.signInURL} />}
            </div>
        );
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        isTranslator: user.selectors.isTranslator(state),
        parameters: navigation.selectors.getNavigationParams(state),
        selectedEntity: entities.selectors.getSelectedEntity(state),
        user: state[NAME],
    };
};

export default (connect(mapStateToProps)(UserControlsBase): any);
