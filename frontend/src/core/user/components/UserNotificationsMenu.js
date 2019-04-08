/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from 'fluent-react';

import UserNotification from './UserNotification';

import './UserNotificationsMenu.css';

import type { UserState } from 'core/user';


type Props = {
    markAllNotificationsAsRead: (element: HTMLElement) => void,
    user: UserState,
};

type State = {|
    visible: boolean,
|};


/**
 * Renders user notifications.
 */
export class UserNotificationsMenuBase extends React.Component<Props, State> {
    notificationsWrapper: { current: any };

    constructor(props: Props) {
        super(props);
        this.notificationsWrapper = React.createRef();

        this.state = {
            visible: false,
        };
    }

    handleClick = () => {
        this.toggleVisibility();
        this.markAllNotificationsAsRead();
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    }

    markAllNotificationsAsRead = () => {
        const element = this.notificationsWrapper.current;

        if (element.classList.contains('unread')) {
            this.props.markAllNotificationsAsRead(element);
        }
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the user menu.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    render() {
        const { user } = this.props;

        if (!user || !user.isAuthenticated) {
            return null;
        }

        let className = 'user-notifications-menu';
        if (user.notifications.has_unread) {
            className += ' unread';
        }

        const notifications = user.notifications.notifications;

        return <div
            className={ className }
            ref={ this.notificationsWrapper }
        >
            <div
                className="selector"
                onClick={ this.handleClick }
            >
                <i className="icon far fa-bell fa-fw"></i>
            </div>

            { !this.state.visible ? null :
            <div className="menu">
                <ul className="notification-list">
                { notifications.length ?
                    notifications.map((notification, index) => {
                        return <UserNotification
                            notification={ notification }
                            key={ index }
                        />;
                    })
                    :
                    <li className="no">
                        <i className="icon fa fa-bell fa-fw"></i>
                        <Localized
                            id="user-UserNotificationsMenu--no-notifications-title"
                        >
                            <p className="title">No new notifications.</p>
                        </Localized>
                        <Localized
                            id="user-UserNotificationsMenu--no-notifications-description"
                        >
                            <p className="description">
                                Here you’ll see updates for localizations you contribute to.
                            </p>
                        </Localized>
                    </li>
                }
                </ul>

                <div className="see-all">
                    <Localized
                        id="user-UserNotificationsMenu--see-all-notifications"
                    >
                        <a href="/notifications">See all Notifications</a>
                    </Localized>
                </div>
            </div>
            }
        </div>;
    }
}

export default onClickOutside(UserNotificationsMenuBase);
