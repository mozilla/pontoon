import * as Fluent from '@fluent/react';
import { mount } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import { EditorActions } from '~/context/Editor';
import { Locale } from '~/context/Locale';

import { Term } from './Term';

function mountTerm(props, setEditorSelection) {
  return mount(
    <Locale.Provider value={{ code: 'kg' }}>
      <EditorActions.Provider value={{ setEditorSelection }}>
        <Term {...props} />
      </EditorActions.Provider>
    </Locale.Provider>,
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
    const wrapper = mountTerm({ term: TERM }, sinon.spy());

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('.text').text()).toEqual('text');
    expect(wrapper.find('.part-of-speech').text()).toEqual('partOfSpeech');
    expect(wrapper.find('.definition').text()).toEqual('definition');
    expect(wrapper.find('.usage .content').text()).toEqual('usage');
    expect(wrapper.find('.translation').text()).toEqual('translation');
  });

  it('calls the addTextToEditorTranslation function on click', () => {
    const spy = sinon.spy();
    const wrapper = mountTerm({ term: TERM }, spy);

    wrapper.find('li').simulate('click');
    expect(spy.called).toEqual(true);
  });

  it('does not call the addTextToEditorTranslation function if term not translated', () => {
    const spy = sinon.spy();
    const wrapper = mountTerm({ term: { ...TERM, translation: '' } }, spy);

    wrapper.find('li').simulate('click');
    expect(spy.called).toEqual(false);
  });

  it('does not call the addTextToEditorTranslation function if read-only editor', () => {
    const spy = sinon.spy();
    const wrapper = mountTerm({ isReadOnlyEditor: true, term: TERM }, spy);

    wrapper.find('li').simulate('click');
    expect(spy.called).toEqual(false);
  });
});
