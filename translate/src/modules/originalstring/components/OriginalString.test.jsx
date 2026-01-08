import ftl from '@fluent/dedent';
import React from 'react';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { OriginalString } from './OriginalString';

const ENTITY = {
  format: 'fluent',
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
      <EntityView.Provider value={{ entity: ENTITY }}>
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

    expect(wrapper.find('.original').children().text()).toMatch(
      /^Hello\W*\nSimple\W*\nString$/,
    );
  });

  it('calls the selectTerms function on placeable click', () => {
    const spy = vi.fn();
    const wrapper = mountOriginalString(spy);

    wrapper.find('.original').simulate('click');
    expect(spy).not.toHaveBeenCalled();

    wrapper.find('.original mark').at(0).simulate('click');
    expect(spy).toHaveBeenCalled();
  });
});
