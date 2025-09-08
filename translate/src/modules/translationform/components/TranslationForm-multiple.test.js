import ftl from '@fluent/dedent';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';
import {describe,it,expect} from "vitest";
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

  const views = Array.from(
    wrapper.find('.translationform').instance().querySelectorAll('.cm-content'),
  ).map((el) => el.cmView.view);

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
    const { views, wrapper } = mountForm(ftl`
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
    expect(wrapper.find('label').at(0).html()).toContain('variant');
    expect(wrapper.find('label').at(1).html()).toContain('another-variant');
  });

  it('renders select expression in attributes properly', () => {
    const { views, wrapper } = mountForm(ftl`
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
    expect(wrapper.find('input')).toHaveLength(2);

    const l0 = wrapper.find('label').at(0);
    expect(l0.find('span').at(0).html()).toContain('label');
    expect(l0.find('span').at(1).html()).toContain('macosx');

    const l1 = wrapper.find('label').at(1);
    expect(l1.find('span').at(0).html()).toContain('label');
    expect(l1.find('span').at(1).html()).toContain('other');

    const l2 = wrapper.find('label').at(2);
    expect(l2.find('span').at(0).html()).toContain('accesskey');
    expect(l2.find('span').at(1).html()).toContain('macosx');
    expect(wrapper.find('input').at(0).html()).toContain('e');

    const l3 = wrapper.find('label').at(3);
    expect(l3.find('span').at(0).html()).toContain('accesskey');
    expect(l3.find('span').at(1).html()).toContain('other');
    expect(wrapper.find('input').at(1).html()).toContain('s');
  });

  it('renders plural string properly', () => {
    const { views, wrapper } = mountForm(ftl`
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

    const labels = wrapper.find('#translationform--label-with-example');
    expect(labels.at(0).prop('vars')).toEqual({ label: 'one', example: 1 });
    expect(labels.at(1).prop('vars')).toEqual({ label: 'other', example: 2 });
  });

  it('renders plural string in attributes properly', () => {
    const { views, wrapper } = mountForm(ftl`
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

    expect(wrapper.find('label').at(0).find('span').at(0).html()).toContain(
      'label',
    );
    expect(wrapper.find('label').at(1).find('span').at(0).html()).toContain(
      'label',
    );

    const labels = wrapper.find('#translationform--label-with-example');
    expect(labels.at(0).prop('vars')).toEqual({ label: 'one', example: 1 });
    expect(labels.at(1).prop('vars')).toEqual({ label: 'other', example: 2 });
  });

  it('renders access keys properly', () => {
    const { views, wrapper } = mountForm(ftl`
      title = Title
        .label = Candidates
        .accesskey = C
      `);

    expect(views.map((view) => view.state.doc.toString())).toMatchObject([
      'Title',
      'Candidates',
    ]);

    expect(wrapper.find('label').at(1).html()).toContain('label');
    expect(wrapper.find('label').at(2).html()).toContain('accesskey');

    const input = wrapper.find('input');
    expect(input).toHaveLength(1);
    expect(input.prop('value')).toEqual('C');
    expect(input.prop('maxLength')).toEqual(1);

    expect(wrapper.find('.accesskeys')).toHaveLength(1);
    expect(wrapper.find('.accesskeys button')).toHaveLength(8);
    expect(wrapper.find('.accesskeys button').at(0).text()).toEqual('C');
    expect(wrapper.find('.accesskeys button').at(1).text()).toEqual('a');
    expect(wrapper.find('.accesskeys button').at(2).text()).toEqual('n');
    expect(wrapper.find('.accesskeys button').at(3).text()).toEqual('d');
    expect(wrapper.find('.accesskeys button').at(4).text()).toEqual('i');
    expect(wrapper.find('.accesskeys button').at(5).text()).toEqual('t');
    expect(wrapper.find('.accesskeys button').at(6).text()).toEqual('e');
    expect(wrapper.find('.accesskeys button').at(7).text()).toEqual('s');
  });

  it('does not render accesskey buttons if no candidates can be generated', () => {
    const { wrapper } = mountForm(ftl`
      title =
        .label = { reference }
        .accesskey = C
      `);

    expect(wrapper.find('.accesskeys button')).toHaveLength(0);
  });

  it('does not render the access key UI if access key is longer than 1 character', () => {
    const { wrapper } = mountForm(ftl`
      title =
        .label = Candidates
        .accesskey = { reference }
      `);

    expect(wrapper.find('.accesskeys')).toHaveLength(0);
  });

  it('updates the translation when setEditorSelection is passed', async () => {
    const { actions, getResult, wrapper } = mountForm(ftl`
      title = Value
        .label = Something
      `);
    act(() => actions.setEditorSelection('Add'));
    wrapper.update();

    const result = getResult();
    expect(result[0].value).toEqual('ValueAdd');
    expect(result[1].value).toEqual('Something');
  });
});
