import React from 'react';
import { shallow } from 'enzyme';

import Metadata from './Metadata';

const ENTITY = {
  pk: 42,
  original: 'le test',
  original_plural: 'les tests',
  comment: 'my comment',
  path: 'path/to/RESOURCE',
  source: [['file_source.rs', '31']],
  translation: [{ string: 'the test' }, { string: 'plural' }],
  project: {
    slug: 'callme',
    name: 'CallMe',
  },
};
const LOCALE = {
  code: 'kg',
  cldrPlurals: [1, 3, 5],
};

const USER = {
  user: 'A_Ludgate',
};

function createShallowMetadata(entity = ENTITY, pluralForm = -1) {
  return shallow(
    <Metadata
      entity={entity}
      locale={LOCALE}
      pluralForm={pluralForm}
      user={USER}
    />,
  );
}

describe('<Metadata>', () => {
  it('renders correctly', () => {
    const wrapper = createShallowMetadata();

    expect(wrapper.find('SourceArray').dive().text()).toContain(
      ENTITY.source[0][0],
    );
    expect(wrapper.find('EntityComment').dive().props().children).toContain(
      ENTITY.comment,
    );

    expect(
      wrapper.find('#entitydetails-Metadata--resource a.resource-path').text(),
    ).toContain(ENTITY.path);
  });

  it('does not require a comment', () => {
    const wrapper = createShallowMetadata({
      ...ENTITY,
      ...{ comment: '' },
    });

    expect(wrapper.find('SourceArray').dive().text()).toContain(
      ENTITY.source[0][0],
    );
    expect(wrapper.find('EntityComment').dive().props().children).not.toContain(
      ENTITY.comment,
    );
  });

  it('does not require a source', () => {
    const wrapper = createShallowMetadata({ ...ENTITY, ...{ source: [] } });

    expect(wrapper.find('SourceArray').dive().text()).not.toContain(
      ENTITY.source[0][0],
    );
    expect(wrapper.find('EntityComment').dive().props().children).toContain(
      ENTITY.comment,
    );
  });

  it('handles sources as an object with examples', () => {
    const withSourceAsObject = {
      source: {
        arg1: {
          content: '',
          example: 'example_1',
        },
        arg2: {
          content: '',
          example: 'example_2',
        },
      },
    };
    const wrapper = createShallowMetadata({
      ...ENTITY,
      ...withSourceAsObject,
    });

    expect(wrapper.find('SourceObject').dive().props().children).toBe(
      '$ARG1$: example_1, $ARG2$: example_2',
    );
  });

  it('handles sources as an object without examples', () => {
    const withSourceAsObject = {
      source: {
        arg1: {
          content: '',
        },
        arg2: {
          content: '',
        },
      },
    };
    const wrapper = createShallowMetadata({
      ...ENTITY,
      ...withSourceAsObject,
    });

    expect(wrapper.find('SourceObject').dive().props().children).toBe('');
  });
});
