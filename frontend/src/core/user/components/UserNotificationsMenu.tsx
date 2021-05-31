import * as React from 'react';
import { Localized } from '@fluent/react';

import './UserNotificationsMenu.css';

import api from 'core/api';

import UserNotification from './UserNotification';

import { useOnDiscard } from 'core/utils';

import type { UserState, Notification } from 'core/user';

type Props = {
    markAllNotificationsAsRead: () => void;
    user: UserState;
};

type State = {
    visible: boolean;
};

type UserNotificationsMenuProps = {
    notifications: Array<Notification>;
    onDiscard: () => void;
};

export function UserNotificationsMenu({
    notifications,
    onDiscard,
}: UserNotificationsMenuProps): React.ReactElement<'div'> {
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
    State
> {
    constructor(props: Props) {
        super(props);

        this.state = {
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

        api.uxaction.log(
            'Render: Unread notifications icon',
            'Notifications 1.0',
            {
                pathname: window.location.pathname,
            },
        );
    }

    handleClick: () => void = () => {
        if (!this.state.visible) {
            api.uxaction.log('Click: Notifications icon', 'Notifications 1.0', {
                pathname: window.location.pathname,
                unread: this.props.user.notifications.has_unread,
            });
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

    render(): null | React.ReactElement<'div'> {
        const { user } = this.props;

        if (!user || !user.isAuthenticated) {
            return null;
        }

        return (
            <div className='user-notifications-menu'>
                <div className='selector' onClick={this.handleClick}>
                    <i className='icon far fa-bell fa-fw'></i>
                    {user.notifications.has_unread && (
                        <i className='badge'>
                            {user.notifications.unread_count}
                        </i>
                    )}
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
