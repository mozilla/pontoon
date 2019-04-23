/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './NotificationPanel.css';

import { NAME } from '..';

import type { NotificationState } from '../reducer';


type Props = {|
    notification: NotificationState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

type State = {|
    hiding: boolean,
|};


/**
 */
export class NotificationPanelBase extends React.Component<InternalProps, State> {
    hideTimeout: TimeoutID;

    constructor(props: InternalProps) {
        super(props);

        this.state = {
            hiding: false,
        };
    }

    componentDidUpdate(prevProps: InternalProps) {
        if (
            this.props.notification.message &&
            prevProps.notification.message !== this.props.notification.message
        ) {
            this.setState({ hiding: false });
            this.hideTimeout = setTimeout(() => {
                this.hide();
            }, 2000);
        }
    }

    hide = () => {
        clearTimeout(this.hideTimeout);
        this.setState({ hiding: true });
    }

    render() {
        const { notification } = this.props;

        let hideClass = '';
        if (notification.message) {
            hideClass = ' showing';
        }
        if (this.state.hiding) {
            hideClass = ' hide';
        }

        const notif = notification.message;

        return <div className={ 'notification-panel' + hideClass } onClick={ this.hide }>
            { !notif ? null :
                <span className={ notif.type }>
                    { notif.message }
                </span>
            }
        </div>
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        notification: state[NAME],
    };
};

export default connect(mapStateToProps)(NotificationPanelBase);
