import React from 'react';
import * as Hooks from '../hooks';
import { useReadonlyEditor } from './useReadonlyEditor';
import { renderHook } from '@testing-library/react-hooks';
import {describe,it,expect,beforeAll,afterAll,vi} from "vitest";
let useContextSpy;
let useAppSelectorSpy;
beforeAll(() => {
  useContextSpy = vi.spyOn(React, 'useContext').mockReturnValue({ entity: 42 });
  useAppSelectorSpy = vi.spyOn(Hooks, 'useAppSelector');
});
afterAll(() => {
  useContextSpy.mockRestore();
  useAppSelectorSpy.mockRestore();
});

function fakeSelector(readonly, isAuthenticated) {
  useContextSpy.mockReturnValue({ entity: { pk: 42, original: 'hello', readonly } });
  return (cb) => cb({ user: { isAuthenticated } });
}

describe('useReadonlyEditor', () => {
  it('returns true if user not authenticated', () => {
    useAppSelectorSpy.mockImplementation(fakeSelector(false, false));
    const {result} = renderHook(() => useReadonlyEditor());
    expect(result.current).toBeTruthy();
  });

  it('returns true if entity read-only', () => {
   useAppSelectorSpy.mockImplementation(fakeSelector(true, true));
   const {result} = renderHook(()=> 
  useReadonlyEditor())
    expect(result.current).toBeTruthy();
  });

  it('returns true if entity not read-only and user authenticated', () => {
    useAppSelectorSpy.mockImplementation(fakeSelector(false, true));
    const {result} = renderHook(() => useReadonlyEditor());
    expect(result.current).toBeTruthy();
  });
});
