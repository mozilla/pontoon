import React from 'react';
import { shallow } from 'enzyme';

import { UserNotificationsMenuBase } from './UserNotificationsMenu';
import UserNotification from './UserNotification';

describe('<UserNotificationsMenuBase>', () => {
    it('hides the notifications icon when the user is logged out', () => {
        const user = {
            isAuthenticated: false,
        };
        const wrapper = shallow(<UserNotificationsMenuBase user={user} />);

        expect(wrapper.find('.user-notifications-menu')).toHaveLength(0);
    });

    it('shows the notifications icon when the user is logged in', () => {
        const user = {
            isAuthenticated: true,
            notifications: {
                has_unread: false,
                notifications: [],
            },
        };
        const wrapper = shallow(<UserNotificationsMenuBase user={user} />);

        expect(wrapper.find('.user-notifications-menu')).toHaveLength(1);
    });

    it('highlights the notifications icon when the user has unread notifications', () => {
        const user = {
            isAuthenticated: true,
            notifications: {
                has_unread: true,
                notifications: [],
            },
        };
        const wrapper = shallow(<UserNotificationsMenuBase user={user} />);

        expect(wrapper.find('.user-notifications-menu.unread')).toHaveLength(1);
    });

    it('shows empty notifications menu if user has no notifications', () => {
        const user = {
            isAuthenticated: true,
            notifications: {
                has_unread: false,
                notifications: [],
            },
        };
        const wrapper = shallow(<UserNotificationsMenuBase user={user} />);
        wrapper.instance().setState({ visible: true });

        expect(
            wrapper.find('.notification-list .user-notification'),
        ).toHaveLength(0);
        expect(wrapper.find('.notification-list .no')).toHaveLength(1);
    });

    it('shows a notification in the notifications menu', () => {
        const user = {
            isAuthenticated: true,
            notifications: {
                has_unread: false,
                notifications: [
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
                ],
            },
        };

        const wrapper = shallow(<UserNotificationsMenuBase user={user} />);
        wrapper.instance().setState({ visible: true });

        expect(wrapper.find('.notification-list .no')).toHaveLength(0);
        expect(wrapper.find(UserNotification)).toHaveLength(1);
    });
});
