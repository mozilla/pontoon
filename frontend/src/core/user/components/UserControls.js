/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import * as navigation from 'core/navigation';
import AppSwitcher from './AppSwitcher';
import SignIn from './SignIn';
import UserAutoUpdater from './UserAutoUpdater';
import UserMenu from './UserMenu';
import { actions, NAME } from '..';

import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';


type Props = {|
    parameters: NavigationParams,
    router: Object,
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

    signUserOut = () => {
        const { user } = this.props;
        this.props.dispatch(actions.signOut(user.signOutURL));
    }

    render() {
        const { parameters, router, user } = this.props;

        return <div className='user-controls'>
            <UserAutoUpdater getUserData={ this.getUserData } />

            <UserMenu
                parameters={ parameters }
                signOut={ this.signUserOut }
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
        parameters: navigation.selectors.getNavigationParams(state),
        router: state.router,
        user: state[NAME],
    };
};

export default connect(mapStateToProps)(UserControlsBase);
