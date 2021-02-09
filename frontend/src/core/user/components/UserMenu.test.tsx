import React from 'react';
import { shallow } from 'enzyme';

import FileUpload from './FileUpload';
import SignOut from './SignOut';
import UserMenuBase, { UserMenu } from './UserMenu';

import { findLocalizedById } from 'test/utils';

function createShallowUserMenu({
    isAdmin = false,
    isReadOnly = false,
    isTranslator = true,
    isAuthenticated = true,
    locale = 'mylocale',
    project = 'myproject',
    resource = 'myresource',
} = {}) {
    return shallow(
        <UserMenu
            isReadOnly={isReadOnly}
            isTranslator={isTranslator}
            user={{ isAuthenticated, isAdmin }}
            parameters={{ locale, project, resource }}
        />,
    );
}

describe('<UserMenu>', () => {
    it('shows the right menu items when the user is logged in', () => {
        const wrapper = createShallowUserMenu({
            locale: 'locale',
            project: 'project',
        });

        expect(wrapper.find('.details')).toHaveLength(1);
        expect(wrapper.find('a[href="/settings/"]')).toHaveLength(1);
        expect(wrapper.find(SignOut)).toHaveLength(1);
    });

    it('hides the right menu items when the user is logged out', () => {
        const wrapper = createShallowUserMenu({ isAuthenticated: false });

        expect(wrapper.find('.details')).toHaveLength(0);
        expect(wrapper.find('a[href="/settings/"]')).toHaveLength(0);
        expect(wrapper.find(SignOut)).toHaveLength(0);
    });

    it('shows upload & download menu items', () => {
        const wrapper = createShallowUserMenu();

        expect(wrapper.find(FileUpload)).toHaveLength(1);
        expect(
            findLocalizedById(wrapper, 'user-UserMenu--download-translations'),
        ).toHaveLength(1);
    });

    it('hides upload & download menu items when translating all projects', () => {
        const wrapper = createShallowUserMenu({ project: 'all-projects' });

        expect(wrapper.find(FileUpload)).toHaveLength(0);
        expect(
            findLocalizedById(wrapper, 'user-UserMenu--download-translations'),
        ).toHaveLength(0);
    });

    it('hides upload & download menu items when translating all resources', () => {
        const wrapper = createShallowUserMenu({ resource: 'all-resources' });

        expect(wrapper.find(FileUpload)).toHaveLength(0);
        expect(
            findLocalizedById(wrapper, 'user-UserMenu--download-translations'),
        ).toHaveLength(0);
    });

    it('hides upload menu item for users without permission to review translations', () => {
        const wrapper = createShallowUserMenu({ isTranslator: false });

        expect(wrapper.find(FileUpload)).toHaveLength(0);
    });

    it('hides upload menu for read-only strings', () => {
        const wrapper = createShallowUserMenu({ isReadOnly: true });

        expect(wrapper.find(FileUpload)).toHaveLength(0);
    });

    it('shows the admin menu items when the user is an admin', () => {
        const wrapper = createShallowUserMenu({ isAdmin: true });

        expect(wrapper.find('a[href="/admin/"]')).toHaveLength(1);
        expect(
            wrapper.find('a[href="/admin/projects/myproject/"]'),
        ).toHaveLength(1);
    });
});

function createShallowUserMenuBase({
    isAdmin = false,
    isAuthenticated = true,
} = {}) {
    return shallow(<UserMenuBase user={{ isAuthenticated, isAdmin }} />);
}

describe('<UserMenuBase>', () => {
    it('shows the user avatar when the user is logged in', () => {
        const wrapper = createShallowUserMenuBase();

        expect(wrapper.find('img')).toHaveLength(1);
        expect(wrapper.find('.menu-icon')).toHaveLength(0);
    });

    it('shows the general menu icon when the user is logged out', () => {
        const wrapper = createShallowUserMenuBase({ isAuthenticated: false });

        expect(wrapper.find('img')).toHaveLength(0);
        expect(wrapper.find('.menu-icon')).toHaveLength(1);
    });

    it('toggles the user menu when clicking the user avatar', () => {
        const wrapper = createShallowUserMenuBase();
        expect(wrapper.find('UserMenu')).toHaveLength(0);

        wrapper.find('.selector').simulate('click');
        expect(wrapper.find('UserMenu')).toHaveLength(1);

        wrapper.find('.selector').simulate('click');
        expect(wrapper.find('UserMenu')).toHaveLength(0);
    });
});
