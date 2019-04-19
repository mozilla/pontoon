/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './NotificationPanel.css';

import { actions, NAME } from '..';

import type { NotificationState } from '../reducer';


type Props = {|
    notification: NotificationState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 */
export class NotificationPanelBase extends React.Component<InternalProps> {
    constructor(props: InternalProps) {
        super(props);

        this.state = {
            hiding: false,
        };
    }

    componentDidUpdate(prevProps: InternalProps) {
        if (prevProps.notification.messages[0] !== this.props.notification.messages[0]) {
            this.setState({ hiding: false });
            setTimeout(() => {
                this.setState({ hiding: true });
            }, 2000);
        }
    }

    render() {
        const { notification } = this.props;

        let hideClass = '';
        if (notification.messages.length) {
            hideClass = ' showing';
        }
        if (this.state.hiding) {
            hideClass = ' hide';
        }

        return <ul className={ 'notification-panel' + hideClass }>
            { notification.messages.map((notif, index) => {
                return <li key={ index } className={ notif.type }>
                    { notif.message }
                </li>;
            }) }
        </ul>
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        notification: state[NAME],
    };
};

export default connect(mapStateToProps)(NotificationPanelBase);
