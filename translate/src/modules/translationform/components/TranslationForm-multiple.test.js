import ftl from '@fluent/dedent';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';

import { EditorActions, EditorProvider } from '~/context/Editor';
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
    format: 'ftl',
    original: 'my-message = Hello',
    translation: [{ string }],
  };

  let actions;
  const Spy = () => {
    actions = useContext(EditorActions);
    return null;
  };

  const wrapper = mountComponentWithStore(
    () => (
      <Locale.Provider value={DEFAULT_LOCALE}>
        <MockLocalizationProvider>
          <EntityView.Provider value={{ entity, pluralForm: 0 }}>
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

  return [wrapper, actions];
}

describe('<TranslationForm> with multiple fields', () => {
  it('renders textarea for a value and each attribute', () => {
    const [wrapper] = mountForm(ftl`
      message = Value
        .attr-1 = And
        .attr-2 = Attributes
      `);

    expect(wrapper.find('textarea')).toHaveLength(3);
    expect(wrapper.find('textarea').at(0).html()).toContain('Value');
    expect(wrapper.find('textarea').at(1).html()).toContain('And');
    expect(wrapper.find('textarea').at(2).html()).toContain('Attributes');
  });

  it('renders select expression properly', () => {
    const [wrapper] = mountForm(ftl`
      my-entry =
        { PLATFORM() ->
            [variant] Hello!
           *[another-variant] World!
        }
      `);

    expect(wrapper.find('textarea')).toHaveLength(2);

    expect(wrapper.find('label').at(0).html()).toContain('variant');
    expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');

    expect(wrapper.find('label').at(1).html()).toContain('another-variant');
    expect(wrapper.find('textarea').at(1).html()).toContain('World!');
  });

  it('renders select expression in attributes properly', () => {
    const [wrapper] = mountForm(ftl`
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

    expect(wrapper.find('textarea')).toHaveLength(2);
    expect(wrapper.find('input')).toHaveLength(2);

    const l0 = wrapper.find('label').at(0);
    expect(l0.find('span').at(0).html()).toContain('label');
    expect(l0.find('span').at(1).html()).toContain('macosx');
    expect(wrapper.find('textarea').at(0).html()).toContain('Preferences');

    const l1 = wrapper.find('label').at(1);
    expect(l1.find('span').at(0).html()).toContain('label');
    expect(l1.find('span').at(1).html()).toContain('other');
    expect(wrapper.find('textarea').at(1).html()).toContain('Options');

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
    const [wrapper] = mountForm(ftl`
      my-entry =
        { $num ->
            [one] Hello!
           *[other] World!
        }
      `);

    expect(wrapper.find('textarea')).toHaveLength(2);

    expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');

    expect(
      wrapper.find('#translationform--label-with-example').at(0).prop('vars'),
    ).toEqual({ label: 'one', example: 1 });

    expect(wrapper.find('textarea').at(1).html()).toContain('World!');

    expect(
      wrapper.find('#translationform--label-with-example').at(1).prop('vars'),
    ).toEqual({ label: 'other', example: 2 });
  });

  it('renders plural string in attributes properly', () => {
    const [wrapper] = mountForm(ftl`
      my-entry =
        .label =
            { $num ->
                [one] Hello!
               *[other] World!
            }
        .attr = Foo
      `);

    expect(wrapper.find('textarea')).toHaveLength(3);

    expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');

    expect(wrapper.find('label').at(0).find('span').at(0).html()).toContain(
      'label',
    );

    expect(
      wrapper.find('#translationform--label-with-example').at(0).prop('vars'),
    ).toEqual({ label: 'one', example: 1 });

    expect(wrapper.find('textarea').at(1).html()).toContain('World!');

    expect(wrapper.find('label').at(1).find('span').at(0).html()).toContain(
      'label',
    );

    expect(
      wrapper.find('#translationform--label-with-example').at(1).prop('vars'),
    ).toEqual({ label: 'other', example: 2 });
  });

  it('renders access keys properly', () => {
    const [wrapper] = mountForm(ftl`
      title = Title
        .label = Candidates
        .accesskey = C
      `);

    expect(wrapper.find('textarea')).toHaveLength(2);
    expect(wrapper.find('input')).toHaveLength(1);

    expect(wrapper.find('label').at(1).html()).toContain('label');
    expect(wrapper.find('textarea').at(1).prop('value')).toEqual('Candidates');

    expect(wrapper.find('label').at(2).html()).toContain('accesskey');
    expect(wrapper.find('input').prop('value')).toEqual('C');
    expect(wrapper.find('input').prop('maxLength')).toEqual(1);

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
    const [wrapper] = mountForm(ftl`
      title =
        .label = { reference }
        .accesskey = C
      `);

    expect(wrapper.find('.accesskeys button')).toHaveLength(0);
  });

  it('does not render the access key UI if access key is longer than 1 character', () => {
    const [wrapper] = mountForm(ftl`
      title =
        .label = Candidates
        .accesskey = { reference }
      `);

    expect(wrapper.find('.accesskeys')).toHaveLength(0);
  });

  it('updates the translation when setEditorSelection is passed', async () => {
    const [wrapper, actions] = mountForm(ftl`
      title = Value
        .label = Something
      `);
    act(() => actions.setEditorSelection('Add'));
    wrapper.update();

    expect(wrapper.find('textarea').at(0).prop('value')).toEqual('ValueAdd');
    expect(wrapper.find('textarea').at(1).prop('value')).toEqual('Something');
  });
});
