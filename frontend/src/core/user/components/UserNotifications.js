/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from 'fluent-react';

import Notification from './Notification';

import './UserNotifications.css';

import type { UserState } from 'core/user';


type Props = {
    user: UserState,
};

type State = {|
    visible: boolean,
|};


/**
 * Renders user notifications.
 */
export class UserNotificationsBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
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

        let className = 'user-notifications';
        if (user.notifications.has_unread) {
            className += ' unread';
        }

        const notifications = user.notifications.notifications;

        return <div className={ className }>
            <div
                className="selector"
                onClick={ this.toggleVisibility }
            >
                <i className="icon far fa-bell fa-fw"></i>
            </div>

            { !this.state.visible ? null :
            <div className="menu">
                <ul className="notification-list">
                { notifications.length ?
                    notifications.map((notification, index) => {
                        return <Notification
                            notification={ notification }
                            key={ index }
                        />;
                    })
                    :
                    <li className="no">
                        <i className="icon fa fa-bell fa-fw"></i>
                        <Localized
                            id="user-UserNotifications--no-notifications-title"
                        >
                            <p className="title">No new notifications.</p>
                        </Localized>
                        <Localized
                            id="user-UserNotifications--no-notifications-description"
                        >
                            <p className="description">Here you’ll see updates for localizations you contribute to.</p>
                        </Localized>
                    </li>
                }
                </ul>

                <ul>
                    <li className="horizontal-separator"></li>

                    <li className="see-all">
                        <Localized
                            id="user-UserNotifications--see-all-notifications"
                        >
                            <a href="/notifications">See all Notifications</a>
                        </Localized>
                    </li>
                </ul>
            </div>
            }
        </div>;
    }
}

export default onClickOutside(UserNotificationsBase);
