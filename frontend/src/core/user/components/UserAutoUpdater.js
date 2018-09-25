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

type State = {|
    timer: ?IntervalID,
|};


/**
 * Regularly fetch user data to keep it up-to-date with the server.
 */
export class UserAutoUpdaterBase extends React.Component<InternalProps, State> {
    constructor() {
        super();
        this.state = {
            timer: null,
        };
    }

    fetchUserData = () => {
        this.props.dispatch(actions.get());
    }

    componentDidMount() {
        this.fetchUserData();
        const timer = setInterval(this.fetchUserData, 2 * 60 * 1000);
        this.setState({ timer });
    }

    componentWillUnmount() {
        if (this.state.timer) {
            clearInterval(this.state.timer);
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
