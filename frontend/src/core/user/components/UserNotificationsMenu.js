/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from '@fluent/react';

import './UserNotificationsMenu.css';

import UserNotification from './UserNotification';

import type { UserState } from 'core/user';

type Props = {
    markAllNotificationsAsRead: () => void,
    user: UserState,
};

type State = {|
    markAsRead: boolean,
    visible: boolean,
|};

/**
 * Renders user notifications.
 */
export class UserNotificationsMenuBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);

        this.state = {
            markAsRead: false,
            visible: false,
        };
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

    handleClick = () => {
        if (this.state.markAsRead) {
            this.setState({
                markAsRead: false,
            });
        }

        this.toggleVisibility();
        this.markAllNotificationsAsRead();
    };

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    markAllNotificationsAsRead = () => {
        if (this.props.user.notifications.has_unread) {
            this.props.markAllNotificationsAsRead();
        }
    };

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the user menu.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    };

    render() {
        const { user } = this.props;

        if (!user || !user.isAuthenticated) {
            return null;
        }

        let className = 'user-notifications-menu';
        if (this.props.user.notifications.has_unread) {
            className += ' unread';
        } else if (this.state.markAsRead) {
            className += ' read';
        }

        if (this.state.visible) {
            className += ' menu-visible';
        }

        const notifications = user.notifications.notifications;

        return (
            <div className={className}>
                <div className='selector' onClick={this.handleClick}>
                    <i className='icon far fa-bell fa-fw'></i>
                </div>

                {!this.state.visible ? null : (
                    <div className='menu'>
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
                                        <p className='title'>
                                            No new notifications.
                                        </p>
                                    </Localized>
                                    <Localized id='user-UserNotificationsMenu--no-notifications-description'>
                                        <p className='description'>
                                            Here you’ll see updates for
                                            localizations you contribute to.
                                        </p>
                                    </Localized>
                                </li>
                            )}
                        </ul>

                        <div className='see-all'>
                            <Localized id='user-UserNotificationsMenu--see-all-notifications'>
                                <a href='/notifications'>
                                    See all Notifications
                                </a>
                            </Localized>
                        </div>
                    </div>
                )}
            </div>
        );
    }
}

export default onClickOutside(UserNotificationsMenuBase);
