/* @flow */
/* globals IntervalID */

import * as React from 'react';

type Props = {
    getUserData: () => void,
};

/**
 * Regularly fetch user data to keep it up-to-date with the server.
 */
export default class UserAutoUpdater extends React.Component<Props> {
    // @ts-expect-error number
    timer: ?IntervalID;

    fetchUserData: () => void = () => {
        this.props.getUserData();
    };

    componentDidMount() {
        this.fetchUserData();
        this.timer = setInterval(this.fetchUserData, 2 * 60 * 1000);
    }

    componentWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }

    render(): null {
        return null;
    }
}
