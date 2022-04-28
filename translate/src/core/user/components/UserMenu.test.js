import { mount, shallow } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import { Location } from '~/context/location';
import * as Hooks from '~/hooks';
import * as Translator from '~/hooks/useTranslator';

import { findLocalizedById, MockLocalizationProvider } from '~/test/utils';

import { FileUpload } from './FileUpload';
import { SignOut } from './SignOut';
import UserMenuBase, { UserMenu } from './UserMenu';

describe('<UserMenu>', () => {
  beforeAll(() => {
    sinon.stub(Hooks, 'useAppSelector');
    sinon.stub(Translator, 'useTranslator');
  });
  afterAll(() => {
    Hooks.useAppSelector.restore();
    Translator.useTranslator.restore();
  });

  const LOCATION = {
    locale: 'my',
    project: 'proj',
    resource: 'res',
    entity: 42,
  };

  function createUserMenu({
    isAdmin = false,
    isReadOnly = false,
    isTranslator = true,
    isAuthenticated = true,
    location = LOCATION,
  } = {}) {
    Hooks.useAppSelector.callsFake((sel) =>
      sel({
        entities: { entities: [{ pk: 42, readonly: isReadOnly }] },
      }),
    );
    Translator.useTranslator.returns(isTranslator);
    return mount(
      <Location.Provider value={location}>
        <MockLocalizationProvider>
          <UserMenu user={{ isAuthenticated, isAdmin }} />
        </MockLocalizationProvider>
      </Location.Provider>,
    );
  }

  it('shows the right menu items when the user is logged in', () => {
    const wrapper = createUserMenu();

    expect(wrapper.find('.details')).toHaveLength(1);
    expect(wrapper.find('a[href="/settings/"]')).toHaveLength(1);
    expect(wrapper.find(SignOut)).toHaveLength(1);
  });

  it('hides the right menu items when the user is logged out', () => {
    const wrapper = createUserMenu({ isAuthenticated: false });

    expect(wrapper.find('.details')).toHaveLength(0);
    expect(wrapper.find('a[href="/settings/"]')).toHaveLength(0);
    expect(wrapper.find(SignOut)).toHaveLength(0);
  });

  it('shows upload & download menu items', () => {
    const wrapper = createUserMenu();

    expect(wrapper.find(FileUpload)).toHaveLength(1);
    expect(
      findLocalizedById(wrapper, 'user-UserMenu--download-translations'),
    ).toHaveLength(1);
  });

  it('hides upload & download menu items when translating all projects', () => {
    const wrapper = createUserMenu({
      location: { ...LOCATION, project: 'all-projects' },
    });

    expect(wrapper.find(FileUpload)).toHaveLength(0);
    expect(
      findLocalizedById(wrapper, 'user-UserMenu--download-translations'),
    ).toHaveLength(0);
  });

  it('hides upload & download menu items when translating all resources', () => {
    const wrapper = createUserMenu({
      location: { ...LOCATION, resource: 'all-resources' },
    });

    expect(wrapper.find(FileUpload)).toHaveLength(0);
    expect(
      findLocalizedById(wrapper, 'user-UserMenu--download-translations'),
    ).toHaveLength(0);
  });

  it('hides upload menu item for users without permission to review translations', () => {
    const wrapper = createUserMenu({ isTranslator: false });

    expect(wrapper.find(FileUpload)).toHaveLength(0);
  });

  it('hides upload menu for read-only strings', () => {
    const wrapper = createUserMenu({ isReadOnly: true });

    expect(wrapper.find(FileUpload)).toHaveLength(0);
  });

  it('shows the admin menu items when the user is an admin', () => {
    const wrapper = createUserMenu({ isAdmin: true });

    expect(wrapper.find('a[href="/admin/"]')).toHaveLength(1);
    expect(wrapper.find('a[href="/admin/projects/proj/"]')).toHaveLength(1);
  });
});

describe('<UserMenuBase>', () => {
  function createShallowUserMenuBase({ isAuthenticated = true } = {}) {
    return shallow(<UserMenuBase user={{ isAuthenticated }} />);
  }

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
