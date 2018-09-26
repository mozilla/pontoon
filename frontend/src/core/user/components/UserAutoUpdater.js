/* @flow */
/* globals IntervalID */

import * as React from 'react';
import { connect } from 'react-redux';

import { actions } from '..';


type Props = {
};

type InternalProps = {
    ...Props,
    dispatch: Function,
};


/**
 * Regularly fetch user data to keep it up-to-date with the server.
 */
export class UserAutoUpdaterBase extends React.Component<InternalProps> {
    timer: ?IntervalID;

    fetchUserData = () => {
        this.props.dispatch(actions.get());
    }

    componentDidMount() {
        this.fetchUserData();
        this.timer = setInterval(this.fetchUserData, 2 * 60 * 1000);
    }

    componentWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }

    render() {
        return null;
    }
}


const mapStateToProps = (): Props => {
    return {};
};

export default connect(mapStateToProps)(UserAutoUpdaterBase);
