/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import * as user from 'core/user';

import AppSwitcher from './AppSwitcher';
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
    router: Object,
    selectedEntity: Entity,
    user: UserState,
|};

type InternalProps = {
    ...Props,
    dispatch: Function,
};


export class UserControlsBase extends React.Component<InternalProps> {
    getUserData = () => {
        this.props.dispatch(actions.get());
    }

    markAllNotificationsAsRead = () => {
        this.props.dispatch(actions.markAllNotificationsAsRead());
    }

    signUserOut = () => {
        const { user } = this.props;
        this.props.dispatch(actions.signOut(user.signOutURL));
    }

    render() {
        const { isTranslator, parameters, router, user, selectedEntity } = this.props;

        const isReadOnly = selectedEntity ? selectedEntity.readonly : true;

        return <div className='user-controls'>
            <UserAutoUpdater getUserData={ this.getUserData } />

            <UserMenu
                isReadOnly={ isReadOnly }
                isTranslator={ isTranslator }
                parameters={ parameters }
                signOut={ this.signUserOut }
                user={ user }
            />

            <UserNotificationsMenu
                markAllNotificationsAsRead={ this.markAllNotificationsAsRead }
                user={ user }
            />

            { user.isAuthenticated ? null :
            <SignIn url={ user.signInURL } />
            }

            { /* To be removed as part of bug 1527853. */ }
            <AppSwitcher router={ router } user={ user } />
        </div>;
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        isTranslator: user.selectors.isTranslator(state),
        parameters: navigation.selectors.getNavigationParams(state),
        router: state.router,
        selectedEntity: entities.selectors.getSelectedEntity(state),
        user: state[NAME],
    };
};

export default connect(mapStateToProps)(UserControlsBase);
