/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './UserNotificationsMenu.css';

import UserNotification from './UserNotification';

import { useOnDiscard } from 'core/utils';

import type { UserState, Notification } from 'core/user';

type Props = {
    logUxAction: (string, ?string, ?any) => void,
    markAllNotificationsAsRead: () => void,
    user: UserState,
};

type State = {|
    markAsRead: boolean,
    visible: boolean,
|};

type UserNotificationsMenuProps = {
    notifications: Array<Notification>,
    onDiscard: (e: SyntheticEvent<any>) => void,
};

export function UserNotificationsMenu({
    notifications,
    onDiscard,
}: UserNotificationsMenuProps): React.Element<'div'> {
    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);

    return (
        <div ref={ref} className='menu'>
            <ul className='notification-list'>
                {notifications.length ? (
                    notifications.map((notification) => {
                        return (
                            <UserNotification
                                notification={notification}
                                key={notification.id}
                            />
                        );
                    })
                ) : (
                    <li className='no'>
                        <i className='icon fa fa-bell fa-fw'></i>
                        <Localized id='user-UserNotificationsMenu--no-notifications-title'>
                            <p className='title'>No new notifications.</p>
                        </Localized>
                        <Localized id='user-UserNotificationsMenu--no-notifications-description'>
                            <p className='description'>
                                Here you’ll see updates for localizations you
                                contribute to.
                            </p>
                        </Localized>
                    </li>
                )}
            </ul>

            <div className='see-all'>
                <Localized id='user-UserNotificationsMenu--see-all-notifications'>
                    <a href='/notifications?referrer=ui'>
                        See all Notifications
                    </a>
                </Localized>
            </div>
        </div>
    );
}

/**
 * Renders user notifications.
 */
export default class UserNotificationsMenuBase extends React.Component<
    Props,
    State,
> {
    constructor(props: Props) {
        super(props);

        this.state = {
            markAsRead: false,
            visible: false,
        };
    }

    componentDidMount() {
        if (!this.props.user.isAuthenticated) {
            return;
        }

        if (!this.props.user.notifications.has_unread) {
            return;
        }

        this.props.logUxAction(
            'Render: Unread notifications icon',
            'Notifications 1.0',
            {
                pathname: window.location.pathname,
            },
        );
    }

    componentDidUpdate(prevProps: Props) {
        if (!this.props.user.isAuthenticated) {
            return;
        }

        if (
            prevProps.user.notifications.has_unread &&
            !this.props.user.notifications.has_unread
        ) {
            this.setState({
                markAsRead: true,
            });
        }
    }

    handleClick: () => void = () => {
        if (this.state.markAsRead) {
            this.setState({
                markAsRead: false,
            });
        }

        if (!this.state.visible) {
            this.props.logUxAction(
                'Click: Notifications icon',
                'Notifications 1.0',
                {
                    pathname: window.location.pathname,
                    unread: this.props.user.notifications.has_unread,
                },
            );
        }

        this.toggleVisibility();
        this.markAllNotificationsAsRead();
    };

    toggleVisibility: () => void = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    markAllNotificationsAsRead: () => void = () => {
        if (this.props.user.notifications.has_unread) {
            this.props.markAllNotificationsAsRead();
        }
    };

    handleDiscard: () => void = () => {
        this.setState({
            visible: false,
        });
    };

    render(): null | React.Element<'div'> {
        const { user } = this.props;

        if (!user || !user.isAuthenticated) {
            return null;
        }

        let className = 'user-notifications-menu';
        if (user.notifications.has_unread) {
            className += ' unread';
        } else if (this.state.markAsRead) {
            className += ' read';
        }

        if (this.state.visible) {
            className += ' menu-visible';
        }

        return (
            <div className={className}>
                <div className='selector' onClick={this.handleClick}>
                    <i className='icon far fa-bell fa-fw'></i>
                </div>

                {this.state.visible && (
                    <UserNotificationsMenu
                        notifications={user.notifications.notifications}
                        onDiscard={this.handleDiscard}
                    />
                )}
            </div>
        );
    }
}
