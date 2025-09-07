/* eslint-disable no-console */
import {describe,it,expect,beforeAll,afterAll,afterEach,vi} from "vitest";
import React from 'react';
import { renderHook } from '@testing-library/react-hooks';
import { usePluralExamples } from './usePluralExamples';
describe('usePluralExamples', () => {
  let consoleErrorSpy;
  let useMemoSpy;
  beforeAll(() => {
  consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    useMemoSpy = vi.spyOn(React, "useMemo").mockImplementation((cb) => cb());
  });
  afterEach(() => {consoleErrorSpy.mockClear();});
  afterAll(() => {
    consoleErrorSpy.mockRestore();
    useMemoSpy.mockRestore();
  });

  it('returns a map of Slovenian plural examples', () => {
 const { result } = renderHook(() =>
      usePluralExamples({
        cldrPlurals: [1, 2, 3, 5],
        pluralRule:
          "(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)",
      })
    );
    expect(result.current).toEqual({ 1: 1, 2: 2, 3: 3, 5: 0 });
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  it('prevents infinite loop if locale plurals are not configured properly', () => {
       const { result } = renderHook(() =>
      usePluralExamples({
        cldrPlurals: [0, 1, 2, 3, 4, 5],
        pluralRule: "(n != 1)",
      })
    );

    expect(result.current).toEqual({ 0: 1, 1: 2 });
    expect(consoleErrorSpy).toHaveBeenCalledTimes(1);
  });
});
