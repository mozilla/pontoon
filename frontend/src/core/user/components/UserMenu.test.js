import React from 'react';
import { shallow } from 'enzyme';

import SignOut from './SignOut';
import { UserMenuBase } from './UserMenu';

import { findLocalizedById } from 'test/utils';


describe('<UserMenuBase>', () => {
    it('shows the user avatar when the user is logged in', () => {
        const wrapper = shallow(
            <UserMenuBase
                user={ { isAuthenticated: true } }
                parameters={ { locale: 'mylocale', project: 'myproject' } }
            />
        );

        expect(wrapper.find('img')).toHaveLength(1);
        expect(wrapper.find('.menu-icon')).toHaveLength(0);
    });

    it('shows the general menu icon when the user is logged out', () => {
        const wrapper = shallow(
            <UserMenuBase
                user={ { isAuthenticated: false } }
                parameters={ { locale: 'mylocale', project: 'myproject' } }
            />
        );

        expect(wrapper.find('img')).toHaveLength(0);
        expect(wrapper.find('.menu-icon')).toHaveLength(1);
    });

    it('shows the right menu items when the user is logged in', () => {
        const wrapper = shallow(
            <UserMenuBase
                user={ { isAuthenticated: true } }
                parameters={ { locale: 'locale', project: 'project' } }
            />
        );
        wrapper.instance().setState({visible: true});

        expect(wrapper.find('.details')).toHaveLength(1);
        expect(wrapper.find('a[href="/settings/"]')).toHaveLength(1);
        expect(wrapper.find(SignOut)).toHaveLength(1);
    });

    it('hides the right menu items when the user is logged out', () => {
        const wrapper = shallow(
            <UserMenuBase
                user={ { isAuthenticated: false } }
                parameters={ { locale: 'mylocale', project: 'myproject' } }
            />
        );
        wrapper.instance().setState({visible: true});

        expect(wrapper.find('.details')).toHaveLength(0);
        expect(wrapper.find('a[href="/settings/"]')).toHaveLength(0);
        expect(wrapper.find(SignOut)).toHaveLength(0);
    });

    it('shows download translations menu item', () => {
        const wrapper = shallow(
            <UserMenuBase
                user={ { isAuthenticated: false } }
                parameters={ { locale: 'mylocale', project: 'myproject' } }
            />
        );
        wrapper.instance().setState({visible: true});

        expect(findLocalizedById(wrapper, 'user-UserMenu--download-translations')).toHaveLength(1);
    });

    it('hides download translations menu item if project is all-projects', () => {
        const wrapper = shallow(
            <UserMenuBase
                user={ { isAuthenticated: false } }
                parameters={ { locale: 'mylocale', project: 'all-projects' } }
            />
        );
        wrapper.instance().setState({visible: true});

        expect(findLocalizedById(wrapper, 'user-UserMenu--download-translations')).toHaveLength(0);
    });

    it('shows the admin menu items when the user is an admin', () => {
        const wrapper = shallow(
            <UserMenuBase
                user={ { isAuthenticated: true, isAdmin: true } }
                parameters={ { locale: 'mylocale', project: 'myproject' } }
            />
        );
        wrapper.instance().setState({visible: true});

        expect(wrapper.find('a[href="/admin/"]')).toHaveLength(1);
        expect(wrapper.find('a[href="/admin/projects/myproject/"]')).toHaveLength(1);
    });
});
