import React , { useContext } from 'react';
import {it,expect,describe,vi,beforeAll,afterAll} from "vitest";
import {render} from "@testing-library/react"
import * as Hooks from '../hooks';
import {renderHook} from '@testing-library/react-hooks';
import {
  EntityView,
  EntityViewProvider,
  useActiveTranslation
} from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';

const ENTITIES = [
  { pk: 1, original: 'hello' },
  { pk: 2, original: 'world' },
  { pk: 3 },
];

describe('<EntityViewProvider', () => {
  let useAppSelectorSpy
  beforeAll(() => {
    useAppSelectorSpy = vi.spyOn(Hooks, "useAppSelector").mockReturnValue(ENTITIES)
  })

  afterAll(() => {
    useAppSelectorSpy.mockRestore()
  })

  it('returns the current entity', () => {
    let view;
    const Spy = () => {
      view = useContext(EntityView);
      return null;
    };

    render(
      <Location.Provider value={{ entity: 1 }}>
        <Locale.Provider value={{ cldrPlurals: [1, 5] }}>
          <EntityViewProvider>
            <Spy />
          </EntityViewProvider>
        </Locale.Provider>
      </Location.Provider>,
    );

    expect(view).toMatchObject({ entity: ENTITIES[0] });

     render(
      <Location.Provider value={{ entity: 2 }}>
        <Locale.Provider value={{ cldrPlurals: [1, 5] }}>
          <EntityViewProvider>
            <Spy />
          </EntityViewProvider>
        </Locale.Provider>
      </Location.Provider>
    )
    expect(view).toMatchObject({ entity: ENTITIES[1] });
  });
});

describe('useActiveTranslation', () => {
   let useContextSpy;
   let useMemoSpy;

   beforeAll(() => {
    useContextSpy = vi.spyOn(React, "useContext")
    useMemoSpy = vi.spyOn(React, "useMemo").mockImplementation((cb) => cb())
  })

  afterAll(() => {
    useContextSpy.mockRestore()
    useMemoSpy.mockRestore()
  })

  it('returns the correct string', () => {
    const wrapper = ({ children }) => (
      <EntityView.Provider
        value={{ entity: { translation: { string: 'world' } } }}
      >
        {children}
      </EntityView.Provider>
    );

    const { result } = renderHook(() => useActiveTranslation(), { wrapper });
    expect(result.current).toEqual({ string: 'world' });
  });

  it('does not return rejected translations', () => {
  const wrapper = ({ children }) => (
      <EntityView.Provider
        value={{
          entity: { translation: { string: 'world', rejected: true } },
        }}
      >
        {children}
      </EntityView.Provider>
    );

    const { result } = renderHook(() => useActiveTranslation(), { wrapper });
    expect(result.current).toBeNull();
  });
});
