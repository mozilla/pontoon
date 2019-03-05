/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './AppSwitcher.css';

import type { UserState } from 'core/user';


type Props = {|
    router: Object,
    user: UserState,
|};


/*
 * A component to allow users to switch between versions of the Translate app.
 *
 * To be removed as part of bug 1527853.
 */
export default class AppSwitcher extends React.Component<Props> {
    render() {
        const { router, user } = this.props;

        if (!user || !user.isAuthenticated) {
            return null;
        }

        const currentURL = router.location.pathname + router.location.search;
        const target = '/toggle-use-translate-next/?next=' + currentURL;

        return <Localized id='user-AppSwitcher--leave-translate-next'>
            <a
                href={ target }
                title='Switch back to the current Translate app'
                className='toggle-translate-next'
            >
                Leave Translate.Next
            </a>
        </Localized>;
    }
}
