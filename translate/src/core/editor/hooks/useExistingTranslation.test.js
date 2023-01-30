import { mount } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import { EditorData } from '~/context/Editor';
import * as Entity from '~/context/EntityView';
import { HistoryData } from '~/context/HistoryData';
import { parseEntry } from '~/utils/message';

import { useExistingTranslation } from './useExistingTranslation';

const ACTIVE_TRANSLATION = { pk: 1 };

const HISTORY_STRING = {
  translations: [
    { pk: 12, string: 'I was there before' },
    { pk: 98, string: 'hello, world!' },
    { pk: 10010, string: '' },
  ],
};

const HISTORY_FLUENT = {
  translations: [
    { pk: 12, string: 'msg = I like { -brand }' },
    { pk: 98, string: 'msg = hello, world!' },
    { pk: 431, string: 'msg = Come on Morty!\n' },
  ],
};

function mountSpy(history, editor) {
  let res;
  const Spy = () => {
    res = useExistingTranslation();
    return null;
  };

  mount(
    <HistoryData.Provider value={history}>
      <EditorData.Provider value={editor}>
        <Spy />
      </EditorData.Provider>
    </HistoryData.Provider>,
  );

  return res;
}

describe('useExistingTranslation', () => {
  beforeAll(() =>
    sinon.stub(Entity, 'useActiveTranslation').returns(ACTIVE_TRANSLATION),
  );
  afterAll(() => Entity.useActiveTranslation.restore());

  it('finds identical initial/active translation', () => {
    const res = mountSpy(HISTORY_STRING, {
      format: 'simple',
      initial: 'something',
      value: 'something',
      view: 'simple',
    });

    expect(res).toBe(ACTIVE_TRANSLATION);
  });

  it('finds identical Fluent initial/active translation', () => {
    const res = mountSpy(HISTORY_FLUENT, {
      format: 'ftl',
      initial: 'msg = something',
      value: parseEntry('msg = something'),
      view: 'simple',
    });

    expect(res).toBe(ACTIVE_TRANSLATION);
  });

  it('finds empty initial/active translation', () => {
    const res = mountSpy(HISTORY_STRING, {
      format: 'simple',
      initial: '',
      value: '',
      view: 'simple',
    });

    expect(res).toBe(ACTIVE_TRANSLATION);
  });

  it('finds identical translation in history', () => {
    const prev0 = HISTORY_STRING.translations[0];
    const res0 = mountSpy(HISTORY_STRING, {
      format: 'simple',
      initial: '',
      value: prev0.string,
      view: 'simple',
    });

    expect(res0).toBe(prev0);

    const prev1 = HISTORY_STRING.translations[1];
    const res1 = mountSpy(HISTORY_STRING, {
      format: 'simple',
      initial: '',
      value: prev1.string,
      view: 'simple',
    });

    expect(res1).toBe(prev1);
  });

  it('finds identical Fluent translation in history', () => {
    const prev0 = HISTORY_FLUENT.translations[0];
    const res0 = mountSpy(HISTORY_FLUENT, {
      format: 'ftl',
      initial: 'msg = something',
      value: parseEntry(prev0.string),
      view: 'simple',
    });

    expect(res0).toBe(prev0);

    const prev1 = HISTORY_FLUENT.translations[1];
    const res1 = mountSpy(HISTORY_FLUENT, {
      format: 'ftl',
      initial: 'msg = something',
      value: parseEntry(prev1.string),
      view: 'simple',
    });

    expect(res1).toBe(prev1);
  });

  it('finds empty translation in history', () => {
    const res = mountSpy(HISTORY_STRING, {
      format: 'simple',
      initial: 'x',
      value: '',
      view: 'simple',
    });

    expect(res).toBe(HISTORY_STRING.translations[2]);
  });

  it('finds a Fluent translation in history from a simplified Fluent string', () => {
    const res = mountSpy(HISTORY_FLUENT, {
      format: 'ftl',
      initial: 'msg = something',
      value: 'Come on Morty!',
      view: 'simple',
    });

    expect(res).toBe(HISTORY_FLUENT.translations[2]);
  });
});
