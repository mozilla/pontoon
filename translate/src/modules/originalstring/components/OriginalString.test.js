import ftl from '@fluent/dedent';
import React from 'react';
import sinon from 'sinon';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { OriginalString } from './OriginalString';

const ENTITY = {
  format: 'ftl',
  original: ftl`
    header =
        .page-title = Hello
        Simple
        String
    `,
};

function mountOriginalString(spy) {
  const store = createReduxStore({ user: { isAuthenticated: true } });
  return mountComponentWithStore(
    () => (
      <EntityView.Provider value={{ entity: ENTITY, hasPluralForms: false }}>
        <EditorActions.Provider value={{ setEditorSelection: spy }}>
          <OriginalString terms={{}} />
        </EditorActions.Provider>
      </EntityView.Provider>
    ),
    store,
  );
}

describe('<OriginalString>', () => {
  it('renders original input as simple string', () => {
    const wrapper = mountOriginalString();

    expect(wrapper.find('.original').children().children().text()).toMatch(
      /^Hello\W*\nSimple\W*\nString$/,
    );
  });

  it('calls the selectTerms function on placeable click', () => {
    const spy = sinon.spy();
    const wrapper = mountOriginalString(spy);

    wrapper.find('.original').simulate('click');
    expect(spy.called).toEqual(false);

    wrapper.find('.original mark').at(0).simulate('click');
    expect(spy.called).toEqual(true);
  });
});
