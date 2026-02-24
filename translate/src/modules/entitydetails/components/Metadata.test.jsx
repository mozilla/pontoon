import React from 'react';
import { Provider } from 'react-redux';

import { Locale } from '~/context/Locale';
import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { Metadata } from './Metadata';
import { render } from '@testing-library/react';

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
const EntityCommentTitle = 'COMMENT';

function createMetadata(entity = ENTITY) {
  const store = createReduxStore({ user: USER });
  return render(
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
    const { getByText } = createMetadata();

    getByText(SRC_LOC);
    getByText(EntityCommentTitle);
    getByText(ENTITY.comment);
    getByText(ENTITY.path);
  });

  it('does not require a comment', () => {
    const { getByText, queryByText } = createMetadata({
      ...ENTITY,
      comment: '',
    });
    getByText(SRC_LOC);
    expect(queryByText(EntityCommentTitle)).toBeNull();
  });

  it('does not require a source', () => {
    const { queryByText, getByText } = createMetadata({ ...ENTITY, meta: [] });
    expect(queryByText(SRC_LOC)).toBeNull();
    getByText(EntityCommentTitle);
    getByText(ENTITY.comment);
  });

  it('finds examples for placeholders with source', () => {
    const { container } = createMetadata({
      ...ENTITY,
      format: 'webext',
      original: `
        .local $MAXIMUM = {$arg2 @source=|$2| @example=5}
        .local $REMAINING = {$arg1 @source=|$1| @example=1}
        {{{$REMAINING @source=|$REMAINING$|}/{$MAXIMUM @source=|$MAXIMUM$|} masks available.}}`,
    });

    expect(
      container.querySelector('div.placeholder .content').textContent,
    ).toBe('$MAXIMUM$: 5, $REMAINING$: 1');
  });

  it('only shows examples for placeholders with source and example', () => {
    const { container } = createMetadata({
      ...ENTITY,
      format: 'webext',
      original: `
        .local $MAXIMUM = {$arg2 @source=|$2|}
        .local $REMAINING = {$arg1 @source=|$1| @example=1}
        {{{$REMAINING}/{$MAXIMUM @source=|$MAXIMUM$|} masks available.}}`,
    });

    expect(container.querySelector('div.placeholder')).toBeNull();
  });
});
