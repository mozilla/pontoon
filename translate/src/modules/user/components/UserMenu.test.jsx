import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import { render,screen, fireEvent } from '@testing-library/react';
import { EntityView } from '../../../context/EntityView';
import { Location } from '../../../context/Location';
import * as Translator from '../../../hooks/useTranslator';
import {
  findLocalizedById,
  MockLocalizationProvider,
  mockMatchMedia,
} from '../../../../src/test/utils';

import { FileUpload } from './FileUpload';
import { SignInOutForm } from './SignInOutForm';
import { UserMenu, UserMenuDialog } from './UserMenu';

describe('<UserMenuDialog>', () => {
  beforeAll(() => {
    mockMatchMedia();
     vi.spyOn(Translator, 'useTranslator');
  });
  afterAll(() => {
     vi.restoreAllMocks();
  });

  const LOCATION = {
    locale: 'my',
    project: 'proj',
    resource: 'res',
    entity: 42,
  };

  function createUserMenu({
    isPM = false,
    isReadOnly = false,
    isTranslator = true,
    isAuthenticated = true,
    location = LOCATION,
  } = {}) {
    Translator.useTranslator.mockReturnValue(isTranslator);
    return render(
      <Location.Provider value={location}>
        <MockLocalizationProvider>
          <EntityView.Provider
            value={{ entity: { pk: 42, readonly: isReadOnly } }}
          >
            <UserMenuDialog user={{ isAuthenticated, isPM }} />
          </EntityView.Provider>
        </MockLocalizationProvider>
      </Location.Provider>,
    );
  }

  it('shows the right menu items when the user is logged in', () => {
    const { container } = createUserMenu();

    expect(container.querySelectorAll(".details")).toHaveLength(1);
    expect(container.querySelectorAll('a[href="/settings/"]')).toHaveLength(1);
    expect(screen.queryByTestId("sign-in-out-form")).toBeInTheDocument();
  });

  it('hides the right menu items when the user is logged out', () => {
    const { container } = createUserMenu({ isAuthenticated: false });

    expect(container.querySelectorAll(".details")).toHaveLength(0);
    expect(container.querySelectorAll('a[href="/settings/"]')).toHaveLength(0);
    expect(screen.queryByTestId("sign-in-out-form")).not.toBeInTheDocument();
  });

  it('shows upload & download menu items', () => {
      const { container } = createUserMenu();

    expect(screen.queryByTestId("file-upload-form")).toBeInTheDocument();
    expect(
      findLocalizedById(container, "user-UserMenu--download-translations")
    ).not.toBeInTheDocument();
  });

  it('hides upload & download menu items when translating all projects', () => {
    const { container } = createUserMenu({
      location: { ...LOCATION, project: "all-projects" },
    });

    expect(screen.queryByTestId("file-upload-form")).not.toBeInTheDocument();
    expect(
      findLocalizedById(container, "user-UserMenu--download-translations")
    ).not.toBeInTheDocument();
  });

  it('hides admin · current project menu item when translating all projects', () => {
   const { container } = createUserMenu({
      location: { ...LOCATION, project: "all-projects" },
      isPM: true,
    });

    expect(
      container.querySelectorAll('a[href="/admin/projects/all-projects/"]')
    ).toHaveLength(0);
  });

  it('shows admin · current project menu item when translating a project', () => {
    const { container } = createUserMenu({ isPM: true });

    expect(
      container.querySelectorAll('a[href="/admin/projects/proj/"]')
    ).toHaveLength(1);
  });

  it('hides upload & download menu items when translating all resources', () => {
     const { container } = createUserMenu({
      location: { ...LOCATION, resource: "all-resources" },
    });

    expect(screen.queryByTestId("file-upload-form")).not.toBeInTheDocument();
    expect(
      findLocalizedById(container, "user-UserMenu--download-translations")
    ).not.toBeInTheDocument();
  });

  it('hides upload menu item for users without permission to review translations', () => {
   const { container } = createUserMenu({ isTranslator: false });

    expect(screen.queryByTestId("file-upload-form")).not.toBeInTheDocument();
  });

  it('hides upload menu for read-only strings', () => {
   const { container } = createUserMenu({ isReadOnly: true });

    expect(screen.queryByTestId("file-upload-form")).not.toBeInTheDocument();
  });

  it('shows the admin menu items when the user is an admin', () => {
   const { container } = createUserMenu({ isPM: true });

    expect(container.querySelectorAll('a[href="/admin/"]')).toHaveLength(1);
    expect(
      container.querySelectorAll('a[href="/admin/projects/proj/"]')
    ).toHaveLength(1);
  });
});

describe('<UserMenu>', () => {
  function createShallowUserMenuBase({ isAuthenticated = true } = {}) {
    return render(<UserMenu user={{ isAuthenticated }} />);
  }

  it('shows the user avatar when the user is logged in', () => {
 const { container } = createShallowUserMenuBase();

    expect(container.querySelectorAll("img")).toHaveLength(1);
    expect(container.querySelectorAll(".menu-icon")).toHaveLength(0);
  });

  it('shows the general menu icon when the user is logged out', () => {
   const { container } = createShallowUserMenuBase({ isAuthenticated: false });

    expect(container.querySelectorAll("img")).toHaveLength(0);
    expect(container.querySelectorAll(".menu-icon")).toHaveLength(1);
  });

it.skip('toggles the user menu when clicking the user avatar', () => { 
  function createShallowUserMenuBase2({ isAuthenticated = true } = {}) 
  { return shallow(<UserMenu user={{ isAuthenticated }} />); }
  const wrapper = createShallowUserMenuBase2(); 
  expect(wrapper.find('UserMenuDialog')).toHaveLength(0); 
  wrapper.find('.selector').simulate('click');
  expect(wrapper.find('UserMenuDialog')).toHaveLength(1); 
  wrapper.find('.selector').simulate('click'); 
  expect(wrapper.find('UserMenuDialog')).toHaveLength(0);
  });
});
