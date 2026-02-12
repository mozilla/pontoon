import ftl from '@fluent/dedent';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';

import { EditorActions, EditorProvider, EditorResult } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { TranslationForm } from './TranslationForm';
import { expect } from 'vitest';

const DEFAULT_LOCALE = {
  direction: 'ltr',
  code: 'kg',
  script: 'Latin',
  cldrPlurals: [1, 5],
};

function mountForm(string) {
  const store = createReduxStore();
  createDefaultUser(store);

  const entity = {
    pk: 0,
    format: 'fluent',
    original: 'my-message = Hello',
    translation: { string },
  };

  let actions, result;
  const Spy = () => {
    actions = useContext(EditorActions);
    result = useContext(EditorResult);
    return null;
  };

  const wrapper = mountComponentWithStore(
    () => (
      <Locale.Provider value={DEFAULT_LOCALE}>
        <MockLocalizationProvider>
          <EntityView.Provider value={{ entity }}>
            <EditorProvider>
              <Spy />
              <TranslationForm />
            </EditorProvider>
          </EntityView.Provider>
        </MockLocalizationProvider>
      </Locale.Provider>
    ),
    store,
  );
  const form = wrapper.container.querySelector('.translationform');
  const views = Array.from(form.querySelectorAll('.cm-content')).map(
    (el) => el.cmView.view,
  );

  return { actions, getResult: () => result, views, wrapper };
}

describe('<TranslationForm> with multiple fields', () => {
  it('renders textarea for a value and each attribute', () => {
    const { views } = mountForm(ftl`
      message = Value
        .attr-1 = And
        .attr-2 = Attributes
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Value',
      'And',
      'Attributes',
    ]);
  });

  it('renders select expression properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      my-entry =
        { PLATFORM() ->
            [variant] Hello!
           *[another-variant] World!
        }
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Hello!',
      'World!',
    ]);
    const labels = container.querySelectorAll('label');
    expect(labels[0]).toHaveTextContent('variant');
    expect(labels[1]).toHaveTextContent('another-variant');
  });

  it('renders select expression in attributes properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      my-entry =
        .label =
            { PLATFORM() ->
                [macosx] Preferences
               *[other] Options
            }
        .accesskey =
            { PLATFORM() ->
                [macosx] e
               *[other] s
            }
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Preferences',
      'Options',
    ]);
    expect(container.querySelectorAll('input')).toHaveLength(2);

    const l0 = container.querySelectorAll('label')[0];
    expect(l0.querySelectorAll('span')[0]).toHaveTextContent('label');
    expect(l0.querySelectorAll('span')[1]).toHaveTextContent('macosx');

    const l1 = container.querySelectorAll('label')[1];
    expect(l1.querySelectorAll('span')[0]).toHaveTextContent('label');
    expect(l1.querySelectorAll('span')[1]).toHaveTextContent('other');

    const l2 = container.querySelectorAll('label')[2];
    expect(l2.querySelectorAll('span')[0]).toHaveTextContent('accesskey');
    expect(l2.querySelectorAll('span')[1]).toHaveTextContent('macosx');
    expect(container.querySelectorAll('input')[0]).toHaveValue('e');

    const l3 = container.querySelectorAll('label')[3];
    expect(l3.querySelectorAll('span')[0]).toHaveTextContent('accesskey');
    expect(l3.querySelectorAll('span')[1]).toHaveTextContent('other');
    expect(container.querySelectorAll('input')[1]).toHaveValue('s');
  });

  it('renders plural string properly', () => {
    const {
      views,
      wrapper: { container, debug },
    } = mountForm(ftl`
      my-entry =
        { $num ->
            [one] Hello!
           *[other] World!
        }
      `);
    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Hello!',
      'World!',
    ]);

    const labels = container.querySelectorAll('label');
    expect(labels[0].querySelectorAll('span')[0]).toHaveTextContent('one');
    expect(labels[0].querySelectorAll('span')[1]).toHaveTextContent('1');

    expect(labels[1].querySelectorAll('span')[0]).toHaveTextContent('other');
    expect(labels[1].querySelectorAll('span')[1]).toHaveTextContent('2');
  });

  it('renders plural string in attributes properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      my-entry =
        .label =
            { $num ->
                [one] Hello!
               *[other] World!
            }
        .attr = Foo
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Hello!',
      'World!',
      'Foo',
    ]);

    const labels = container.querySelectorAll('label');
    expect(labels[0].querySelectorAll('span')[0]).toHaveTextContent('label');
    expect(labels[0].querySelectorAll('span')[1]).toHaveTextContent('one');
    expect(labels[0].querySelectorAll('span')[2]).toHaveTextContent('1');

    expect(labels[1].querySelectorAll('span')[0]).toHaveTextContent('label');
    expect(labels[1].querySelectorAll('span')[1]).toHaveTextContent('other');
    expect(labels[1].querySelectorAll('span')[2]).toHaveTextContent('2');
  });

  it('renders access keys properly', () => {
    const {
      views,
      wrapper: { container },
    } = mountForm(ftl`
      title = Title
        .label = Candidates
        .accesskey = C
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Title',
      'Candidates',
    ]);

    expect(container.querySelectorAll('label')[1]).toHaveTextContent('label');
    expect(container.querySelectorAll('label')[2]).toHaveTextContent(
      'accesskey',
    );

    const input = container.querySelectorAll('input');
    expect(input).toHaveLength(1);
    expect(input[0]).toHaveValue('C');
    expect(input[0]).toHaveAttribute('maxLength', '1');

    expect(container.querySelectorAll('.accesskeys')).toHaveLength(1);
    expect(container.querySelectorAll('.accesskeys button')).toHaveLength(8);
    expect(
      container.querySelectorAll('.accesskeys button')[0],
    ).toHaveTextContent('C');
    expect(
      container.querySelectorAll('.accesskeys button')[1],
    ).toHaveTextContent('a');
    expect(
      container.querySelectorAll('.accesskeys button')[2],
    ).toHaveTextContent('n');
    expect(
      container.querySelectorAll('.accesskeys button')[3],
    ).toHaveTextContent('d');
    expect(
      container.querySelectorAll('.accesskeys button')[4],
    ).toHaveTextContent('i');
    expect(
      container.querySelectorAll('.accesskeys button')[5],
    ).toHaveTextContent('t');
    expect(
      container.querySelectorAll('.accesskeys button')[6],
    ).toHaveTextContent('e');
    expect(
      container.querySelectorAll('.accesskeys button')[7],
    ).toHaveTextContent('s');
  });

  it('does not render accesskey buttons if no candidates can be generated', () => {
    const {
      wrapper: { container },
    } = mountForm(ftl`
      title =
        .label = { reference }
        .accesskey = C
      `);

    expect(container.querySelectorAll('.accesskeys button')).toHaveLength(0);
  });

  it('does not render the access key UI if access key is longer than 1 character', () => {
    const {
      wrapper: { container },
    } = mountForm(ftl`
      title =
        .label = Candidates
        .accesskey = { reference }
      `);

    expect(container.querySelectorAll('.accesskeys')).toHaveLength(0);
  });

  it('updates the translation when setEditorSelection is passed', async () => {
    const { actions, getResult } = mountForm(ftl`
      title = Value
        .label = Something
      `);
    act(() => actions.setEditorSelection('Add'));

    const result = getResult();
    expect(result[0].value).toEqual('ValueAdd');
    expect(result[1].value).toEqual('Something');
  });
});
