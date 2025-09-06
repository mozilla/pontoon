import React from 'react';
import {describe,it,expect,vi,beforeAll,afterAll} from "vitest";
import { Locale } from "../../src/context/Locale";
import { Location } from "../../src/context/Location";
import { USER } from '../modules/user';
import * as Hooks from '../hooks';
import {renderHook} from '@testing-library/react-hooks';
import { useUserBanner } from './useUserBanner';
let useAppSelectorSpy;
let useContextSpy;
beforeAll(() => {
  useAppSelectorSpy = vi.spyOn(Hooks,"useAppSelector");
  useContextSpy = vi.spyOn(React,"useContext").mockReturnValue({ code: 'mylocale', project: 'myproject' })

});
afterAll(() => {
  useAppSelectorSpy.mockRestore();
  useContextSpy.mockRestore();
});

const fakeSelector = (user) => (sel) =>
  sel({
    [USER]: user,
  });
 function wrapper({ children }) {
    return (
      <Locale.Provider value={{ code: "mylocale" }}>
        <Location.Provider value={{ project: "myproject" }}>
          {children}
        </Location.Provider>
      </Locale.Provider>
    );
  }
describe('useUserBanner', () => {
  it('returns empty parameters for non-authenticated users', () => {
  useAppSelectorSpy.mockImplementation(fakeSelector({ isAuthenticated: false }));
  const {result} = renderHook(() => useUserBanner());
    expect(result.current).toStrictEqual(['', '']);
  });

  it('returns [ADMIN, Admin] if user has admin permissions', () => {
    useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    const {result} = renderHook(() => useUserBanner());
    expect(result.current).toStrictEqual(['ADMIN', 'Admin']);
  });

  it('returns [PM, Project Manager] if user is a project manager for the project', () => {
    useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: ['myproject'],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    const {result} = renderHook(() => useUserBanner(),{wrapper});
    expect(result.current).toStrictEqual(['PM', 'Project Manager']);
  });

  it('returns [PM, Project Manager] if user is a project manager for the project, even if user is an Admin', () => {
     useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: ['myproject'],
        managerForLocales: [],
        translatorForLocales: [],
      }),
    );
    const {result} = renderHook(() => useUserBanner(),{wrapper});
    expect(result.current).toStrictEqual(['PM', 'Project Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale', () => {
    useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    const {result} = renderHook(() => useUserBanner(),{wrapper});
    expect(result.current).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale, even if user is an Admin', () => {
    useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        isAdmin: true,
        pmForProjects: [],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    const {result} = renderHook(() => useUserBanner(),{wrapper});
    expect(result.current).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [MNGR, Manager] if user is a manager of the locale, even if user is a Project Manager', () => {
     useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: ['myproject'],
        managerForLocales: ['mylocale'],
        translatorForLocales: [],
      }),
    );
    const {result} = renderHook(() => useUserBanner(),{wrapper});
    expect(result.current).toStrictEqual(['MNGR', 'Team Manager']);
  });

  it('returns [TRNSL, Translator] if user is a translator for the locale', () => {
    useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: ['mylocale'],
      }),
    );
    const {result} = renderHook(() => useUserBanner(),{wrapper});
    expect(result.current).toStrictEqual(['TRNSL', 'Translator']);
  });

  it('returns [NEW, New User] if user created their account within the last 3 months', () => {
    const dateJoined = new Date();
    dateJoined.setMonth(dateJoined.getMonth() - 2);
    useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
        dateJoined: dateJoined,
      }),
    );
    const {result} = renderHook(() => useUserBanner(),{wrapper});
    expect(result.current).toStrictEqual(['NEW', 'New User']);

    // Set join date to be 6 months ago (no longer a new user)
    dateJoined.setMonth(dateJoined.getMonth() - 6);
    useAppSelectorSpy.mockImplementation(
      fakeSelector({
        isAuthenticated: true,
        pmForProjects: [],
        managerForLocales: [],
        translatorForLocales: [],
        dateJoined: dateJoined,
      }),
    );
    const {result: result2} = renderHook(() => useUserBanner(),{wrapper});
    expect(result2.current).toStrictEqual(['', '']);
  });
});
