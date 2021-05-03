import React from 'react';
import sinon from 'sinon';
import { shallow } from 'enzyme';

import UserNotificationsMenuBase, {
    UserNotificationsMenu,
} from './UserNotificationsMenu';
import UserNotification from './UserNotification';

describe('<UserNotificationsMenu>', () => {
    it('shows empty notifications menu if user has no notifications', () => {
        const notifications = [];
        const wrapper = shallow(
            <UserNotificationsMenu notifications={notifications} />,
        );

        expect(
            wrapper.find('.notification-list .user-notification'),
        ).toHaveLength(0);
        expect(wrapper.find('.notification-list .no')).toHaveLength(1);
    });

    it('shows a notification in the notifications menu', () => {
        const notifications = [
            {
                id: 0,
                level: 'level',
                unread: false,
                description: 'description',
                verb: 'verb',
                date: 'Jan 31, 2000 10:20',
                date_iso: '2019-01-31T10:20:00+00:00',
                actor: {
                    anchor: 'actor_anchor',
                    url: 'actor_url',
                },
                target: {
                    anchor: 'target_anchor',
                    url: 'target_url',
                },
            },
        ];

        const wrapper = shallow(
            <UserNotificationsMenu notifications={notifications} />,
        );

        expect(wrapper.find('.notification-list .no')).toHaveLength(0);
        expect(wrapper.find(UserNotification)).toHaveLength(1);
    });
});

describe('<UserNotificationsMenuBase>', () => {
    it('hides the notifications icon when the user is logged out', () => {
        const user = {
            isAuthenticated: false,
            notifications: {
                has_unread: false,
            },
        };
        const wrapper = shallow(<UserNotificationsMenuBase user={user} />);

        expect(wrapper.find('.user-notifications-menu')).toHaveLength(0);
    });

    it('shows the notifications icon when the user is logged in', () => {
        const user = {
            isAuthenticated: true,
            notifications: {
                notifications: [],
            },
        };
        const wrapper = shallow(<UserNotificationsMenuBase user={user} />);

        expect(wrapper.find('.user-notifications-menu')).toHaveLength(1);
    });

    it('highlights the notifications icon when the user has unread notifications and call logUxAction', () => {
        const logUxAction = sinon.spy();
        const user = {
            isAuthenticated: true,
            notifications: {
                has_unread: true,
                notifications: [],
            },
        };
        const wrapper = shallow(
            <UserNotificationsMenuBase user={user} logUxAction={logUxAction} />,
        );

        expect(wrapper.find('.user-notifications-menu.unread')).toHaveLength(1);
        expect(logUxAction.called).toEqual(true);
    });

    it('calls the logUxAction function on click on the icon if menu not visible', () => {
        const logUxAction = sinon.spy();
        const markAllNotificationsAsRead = sinon.spy();
        const user = {
            isAuthenticated: true,
            notifications: {
                has_unread: true,
                notifications: [],
            },
        };
        const wrapper = shallow(
            <UserNotificationsMenuBase
                logUxAction={logUxAction}
                markAllNotificationsAsRead={markAllNotificationsAsRead}
                user={user}
            />,
        );

        wrapper.setState({
            visible: false,
        });
        wrapper.find('.selector').simulate('click');
        expect(logUxAction.called).toEqual(true);
    });
});
