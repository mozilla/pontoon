import * as Fluent from '@fluent/react';
import React from 'react';
import sinon from 'sinon';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { Term } from './Term';

function mountTerm(term, setEditorSelection, isAuthenticated) {
  const store = createReduxStore({ user: { isAuthenticated } });
  return mountComponentWithStore(
    () => (
      <Locale.Provider value={{ code: 'kg' }}>
        <EntityView.Provider value={{ entity: {} }}>
          <EditorActions.Provider value={{ setEditorSelection }}>
            <Term term={term} />
          </EditorActions.Provider>
        </EntityView.Provider>
      </Locale.Provider>
    ),
    store,
  );
}

const TERM = {
  text: 'text',
  partOfSpeech: 'partOfSpeech',
  definition: 'definition',
  usage: 'usage',
  translation: 'translation',
};

describe('<Term>', () => {
  let getSelectionBackup;

  beforeAll(() => {
    getSelectionBackup = window.getSelection;
    window.getSelection = () => null;
    sinon.stub(Fluent, 'Localized').callsFake(({ children }) => children);
  });

  afterAll(() => {
    window.getSelection = getSelectionBackup;
    Fluent.Localized.restore();
  });
  it('renders term correctly', () => {
    const wrapper = mountTerm(TERM, sinon.spy(), true);

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('.text').text()).toEqual('text');
    expect(wrapper.find('.part-of-speech').text()).toEqual('partOfSpeech');
    expect(wrapper.find('.definition').text()).toEqual('definition');
    expect(wrapper.find('.usage .content').text()).toEqual('usage');
    expect(wrapper.find('.translation').text()).toEqual('translation');
  });

  it('calls the addTextToEditorTranslation function on click', () => {
    const spy = sinon.spy();
    const wrapper = mountTerm(TERM, spy, true);

    wrapper.find('li').simulate('click');
    expect(spy.called).toEqual(true);
  });

  it('does not call the addTextToEditorTranslation function if term not translated', () => {
    const spy = sinon.spy();
    const wrapper = mountTerm({ ...TERM, translation: '' }, spy, true);

    wrapper.find('li').simulate('click');
    expect(spy.called).toEqual(false);
  });

  it('does not call the addTextToEditorTranslation function if read-only editor', () => {
    const spy = sinon.spy();
    const wrapper = mountTerm(TERM, spy, false);

    wrapper.find('li').simulate('click');
    expect(spy.called).toEqual(false);
  });
});
