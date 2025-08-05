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

  it('handles sources as an object with examples', () => {
    const phData = {
      arg1: { content: '', example: 'example_1' },
      arg2: { content: '', example: 'example_2' },
    };
    const wrapper = createMetadata({
      ...ENTITY,
      meta: [['placeholders', JSON.stringify(phData)]],
    });

    expect(wrapper.find('div.placeholder .content').text()).toBe(
      '$ARG1$: example_1, $ARG2$: example_2',
    );
  });

  it('handles sources as an object without examples', () => {
    const phData = {
      arg1: { content: '' },
      arg2: { content: '' },
    };
    const wrapper = createMetadata({
      ...ENTITY,
      meta: [['placeholders', JSON.stringify(phData)]],
    });

    expect(wrapper.find('div.placeholder')).toHaveLength(0);
  });
});
