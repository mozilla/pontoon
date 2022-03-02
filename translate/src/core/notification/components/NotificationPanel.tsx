import * as React from 'react';

import './NotificationPanel.css';

import type { NotificationState } from '../reducer';

type Props = {
    notification: NotificationState;
};

type State = {
    hiding: boolean;
};

/**
 * Show a status notification for a short period of time.
 *
 * This supports showing 'info' (in green) or 'error' (in red) notifications,
 * once at a time. The notification will hide after a 2s timeout, or when
 * clicked.
 */
export default class NotificationPanel extends React.Component<Props, State> {
    hideTimeout: number;

    constructor(props: Props) {
        super(props);

        // This state is used to start the in and out animations for
        // notifications.
        this.state = {
            hiding: false,
        };
    }

    componentDidUpdate(prevProps: Props) {
        if (
            this.props.notification.message &&
            prevProps.notification.message !== this.props.notification.message
        ) {
            this.setState({ hiding: false });
            clearTimeout(this.hideTimeout);
            this.hideTimeout = window.setTimeout(() => {
                this.hide();
            }, 2000);
        }
    }

    hide: () => void = () => {
        clearTimeout(this.hideTimeout);
        this.setState({ hiding: true });
    };

    render(): React.ReactElement<'div'> {
        const { notification } = this.props;

        let hideClass = '';
        if (notification.message && !this.state.hiding) {
            hideClass = ' showing';
        }

        const notif = notification.message;

        return (
            <div
                className={'notification-panel' + hideClass}
                onClick={this.hide}
            >
                {!notif ? (
                    <span />
                ) : (
                    <span className={notif.type}>{notif.content}</span>
                )}
            </div>
        );
    }
}
