import { mount } from 'enzyme';
import React from 'react';
import { Provider } from 'react-redux';

import { Locale } from '~/context/Locale';
import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { Metadata } from './Metadata';

const SRC_LOC = 'file_source.rs:31';

const ENTITY = {
  pk: 42,
  key: [],
  original: 'le test',
  comment: 'my comment',
  path: 'path/to/RESOURCE',
  meta: [['reference', SRC_LOC]],
  translation: { string: 'the test' },
  project: {
    slug: 'callme',
    name: 'CallMe',
  },
  date_created: new Date().toISOString(),
};

const LOCALE = {
  code: 'kg',
  cldrPlurals: [1, 3, 5],
};

const TERMS = {
  fetching: false,
  sourceString: '',
  terms: [],
};

const USER = {
  user: 'A_Ludgate',
};

function createMetadata(entity = ENTITY) {
  const store = createReduxStore({ user: USER });
  return mount(
    <Provider store={store}>
      <MockLocalizationProvider>
        <Locale.Provider value={LOCALE}>
          <Metadata entity={entity} terms={TERMS} user={USER} />
        </Locale.Provider>
      </MockLocalizationProvider>
    </Provider>,
  );
}

describe('<Metadata>', () => {
  it('renders correctly', () => {
    const wrapper = createMetadata();

    expect(wrapper.text()).toContain(SRC_LOC);
    expect(wrapper.find('#entitydetails-Metadata--comment').text()).toContain(
      ENTITY.comment,
    );

    expect(
      wrapper.find('#entitydetails-Metadata--context a.resource-path').text(),
    ).toContain(ENTITY.path);
  });

  it('does not require a comment', () => {
    const wrapper = createMetadata({ ...ENTITY, comment: '' });
    expect(wrapper.text()).toContain(SRC_LOC);
    expect(wrapper.find('#entitydetails-Metadata--comment')).toHaveLength(0);
  });

  it('does not require a source', () => {
    const wrapper = createMetadata({ ...ENTITY, meta: [] });
    expect(wrapper.text()).not.toContain(SRC_LOC);
    expect(wrapper.find('#entitydetails-Metadata--comment').text()).toContain(
      ENTITY.comment,
    );
  });

  it('finds examples for placeholders with source', () => {
    const wrapper = createMetadata({
      ...ENTITY,
      format: 'webext',
      original: `
        .local $MAXIMUM = {$arg2 @source=|$2| @example=5}
        .local $REMAINING = {$arg1 @source=|$1| @example=1}
        {{{$REMAINING @source=|$REMAINING$|}/{$MAXIMUM @source=|$MAXIMUM$|} masks available.}}`,
    });

    expect(wrapper.find('div.placeholder .content').text()).toBe(
      '$MAXIMUM$: 5, $REMAINING$: 1',
    );
  });

  it('only shows examples for placeholders with source and example', () => {
    const wrapper = createMetadata({
      ...ENTITY,
      format: 'webext',
      original: `
        .local $MAXIMUM = {$arg2 @source=|$2|}
        .local $REMAINING = {$arg1 @source=|$1| @example=1}
        {{{$REMAINING}/{$MAXIMUM @source=|$MAXIMUM$|} masks available.}}`,
    });

    expect(wrapper.find('div.placeholder')).toHaveLength(0);
  });
});
