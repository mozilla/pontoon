/* eslint-disable @typescript-eslint/no-non-null-assertion */

import * as Fluent from '@fluent/react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import sinon from 'sinon';

import { EditFieldHandle, EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
// @ts-expect-error
import { createReduxStore, MockStore } from '~/test/store';

import { EditField } from './EditField';

function MockEditField({
  defaultValue,
  singleField,
  format,
  fieldRef,
  isAuthenticated = true,
  setResultFromInput = sinon.spy(),
}: {
  defaultValue: string;
  singleField?: boolean;
  format: 'fluent' | 'plain';
  fieldRef?: React.RefObject<EditFieldHandle>;
  isAuthenticated?: boolean;
  setResultFromInput?: EditorActions['setResultFromInput'];
}) {
  const store = createReduxStore({ user: { isAuthenticated, settings: {} } });
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
                  format,
                  original: `key = ${defaultValue}`,
                  translation: {},
                },
              } as EntityView
            }
          >
            <EditorActions.Provider
              value={{ setResultFromInput } as EditorActions}
            >
              <EditField
                ref={fieldRef}
                defaultValue={defaultValue}
                index={0}
                singleField={singleField}
              />
            </EditorActions.Provider>
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
    const spy = sinon.spy();
    const { container } = render(
      <MockEditField
        defaultValue='foo'
        format='fluent'
        setResultFromInput={spy}
      />,
    );
    await userEvent.click(container.querySelector('.cm-line')!);
    await userEvent.keyboard('x{ArrowRight}{ArrowRight}{ArrowRight}  y');
    expect(spy.getCalls()).toMatchObject([
      { args: [0, 'xfoo'] },
      { args: [0, 'xfoo '] },
      { args: [0, 'xfoo  '] },
      { args: [0, 'xfoo  y'] },
    ]);
  });

  it('ignores user input when readonly', async () => {
    const spy = sinon.spy();
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
    expect(spy.getCalls()).toMatchObject([]);
  });

  it('sets the result via ref', async () => {
    const spy = sinon.spy();
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
    expect(spy.getCalls()).toMatchObject([{ args: [0, 'foobar'] }]);
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
