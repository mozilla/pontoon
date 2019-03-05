/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import AppSwitcher from './AppSwitcher';
import SignIn from './SignIn';
import SignOut from './SignOut';
import UserAutoUpdater from './UserAutoUpdater';
import { actions, NAME } from '..';

import type { UserState } from 'core/user';


type Props = {|
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
        const { router, user } = this.props;

        return <div className='user-controls'>
            <UserAutoUpdater getUserData={ this.getUserData } />

            { user.isAuthenticated ?
                <SignOut signOut={ this.signUserOut } /> :
                <SignIn url={ user.signInURL } />
            }

            { /* To be removed as part of bug 1527853. */ }
            <AppSwitcher router={ router } user={ user } />
        </div>;
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        router: state.router,
        user: state[NAME],
    };
};

export default connect(mapStateToProps)(UserControlsBase);
