import * as Fluent from '@fluent/react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

import type { MachineryTranslation } from '~/api/machinery';
import { EditFieldHandle, EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';
// @ts-expect-error
import { createReduxStore, MockStore } from '~/test/store';

import { EditField } from './EditField';

function MockEditField({
  defaultValue,
  singleField,
  format,
  fieldRef,
  isAuthenticated = true,
  setResultFromInput = vi.fn(),
  machinery = [],
  machineryAutocomplete = false,
  query = '',
}: {
  defaultValue: string;
  singleField?: boolean;
  format: 'fluent' | 'plain';
  fieldRef?: React.RefObject<EditFieldHandle>;
  isAuthenticated?: boolean;
  setResultFromInput?: EditorActions['setResultFromInput'];
  machinery?: string[];
  machineryAutocomplete?: boolean;
  query?: string;
}) {
  const store = createReduxStore({
    user: { isAuthenticated, settings: { machineryAutocomplete } },
  });
  const translations = machinery.map(
    (translation) =>
      ({
        sources: ['translation-memory'],
        original: '',
        translation,
      }) as MachineryTranslation,
  );
  return (
    <Fluent.LocalizationProvider
      l10n={{ getString: (id) => id } as Fluent.ReactLocalization}
    >
      <MockStore store={store}>
        <Locale.Provider value={{ code: 'kg' } as Locale}>
          <EntityView.Provider
            value={
              {
                entity: {
                  key: ['key'],
                  format,
                  original: `key = ${defaultValue}`,
                  translation: {},
                },
              } as EntityView
            }
          >
            <SearchData.Provider value={{ query } as SearchData}>
              <MachineryTranslations.Provider
                value={{
                  fetching: false,
                  source: '',
                  composed: [],
                  translations,
                }}
              >
                <EditorActions.Provider
                  value={{ setResultFromInput } as EditorActions}
                >
                  <EditField
                    ref={fieldRef}
                    defaultValue={defaultValue}
                    singleField={singleField}
                  />
                </EditorActions.Provider>
              </MachineryTranslations.Provider>
            </SearchData.Provider>
          </EntityView.Provider>
        </Locale.Provider>
      </MockStore>
    </Fluent.LocalizationProvider>
  );
}

describe('<EditField>', () => {
  let createRangeBackup: () => Range;

  beforeAll(() => {
    createRangeBackup = document.createRange;
    // Hack adopted from https://discuss.codemirror.net/t/working-in-jsdom-or-node-js-natively/138/5
    document.createRange = () =>
      ({
        setEnd() {},
        setStart() {},
        getBoundingClientRect: () => ({ right: 0 }),
        getClientRects: () => ({ length: 0, left: 0, right: 0 }),
      }) as unknown as Range;
  });

  afterAll(() => {
    document.createRange = createRangeBackup;
  });

  it('renders field correctly', () => {
    const { container } = render(
      <MockEditField defaultValue='foo' format='fluent' />,
    );

    const lines = container.querySelectorAll('.cm-line');
    expect(lines).toHaveLength(1);
    expect(lines[0].textContent).toEqual('foo');
  });

  it('sets the result on user input', async () => {
    const res: string[] = [];
    const spy = vi.fn(() => {
      res.push(ref.current!.value);
    });
    const ref = React.createRef<EditFieldHandle>();
    const { container } = render(
      <MockEditField
        defaultValue='foo'
        format='fluent'
        fieldRef={ref}
        setResultFromInput={spy}
      />,
    );
    await userEvent.click(container.querySelector('.cm-line')!);
    await userEvent.keyboard('x{ArrowRight}{ArrowRight}{ArrowRight}  y');
    expect(res).toEqual(['xfoo', 'xfoo ', 'xfoo  ', 'xfoo  y']);
  });

  it('ignores user input when readonly', async () => {
    const spy = vi.fn();
    const { container } = render(
      <MockEditField
        defaultValue='foo'
        format='fluent'
        isAuthenticated={false}
        setResultFromInput={spy}
      />,
    );
    await userEvent.click(container.querySelector('.cm-line')!);
    await userEvent.keyboard('x');
    expect(spy).not.toHaveBeenCalled();
  });

  it('sets the result via ref', async () => {
    const res: string[] = [];
    const spy = vi.fn(() => {
      res.push(ref.current!.value);
    });
    const ref = React.createRef<EditFieldHandle>();
    render(
      <MockEditField
        defaultValue='foo'
        format='fluent'
        fieldRef={ref}
        setResultFromInput={spy}
      />,
    );
    act(() => {
      ref.current!.focus();
      ref.current!.setSelection('bar');
    });
    expect(res).toEqual(['foobar']);
  });

  describe('ghost text', () => {
    const firefox = 'Firefox non riesce a trovare il server';
    const ghost = (container: HTMLElement) =>
      container.querySelector('.ghost-text')?.textContent ?? null;

    function renderField(props: Partial<Parameters<typeof MockEditField>[0]>) {
      const ref = React.createRef<EditFieldHandle>();
      const { container } = render(
        <MockEditField
          defaultValue='Firefox non'
          format='plain'
          fieldRef={ref}
          machinery={[firefox]}
          machineryAutocomplete
          {...props}
        />,
      );
      act(() => ref.current!.focus());
      return { container, ref };
    }

    it('is shown from Machinery suggestions and accepted with Tab', async () => {
      const { container, ref } = renderField({});
      expect(ghost(container)).toBe(' riesce');

      await userEvent.keyboard(' r');
      expect(ghost(container)).toBe('iesce');

      await userEvent.keyboard('{Tab}');
      expect(ref.current!.value).toBe('Firefox non riesce');
      expect(ghost(container)).toBe(' a');
    });

    it('is not shown unless enabled in the settings', async () => {
      const { container } = renderField({ machineryAutocomplete: false });
      await userEvent.keyboard(' r');
      expect(ghost(container)).toBeNull();
    });

    it('is not shown during a Concordance search', async () => {
      const { container } = renderField({ query: 'server' });
      await userEvent.keyboard(' r');
      expect(ghost(container)).toBeNull();
    });

    it('is not shown when readonly', () => {
      const { container } = renderField({ isAuthenticated: false });
      expect(ghost(container)).toBeNull();
    });
  });

  it('does not highlight `% d` as code (#2988)', () => {
    render(<MockEditField defaultValue='{0}% done' format='plain' />);
    const placeholder = screen.getByText(/0/);
    const notPrintf = screen.getByText(/% d/);
    const certainlyText = screen.getByText(/one/);
    expect(notPrintf).not.toBe(placeholder);
    expect(notPrintf).toBe(certainlyText);
  });
});
