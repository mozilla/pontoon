/* eslint-disable no-console */

import React from 'react';
import sinon from 'sinon';
import { usePluralExamples } from './usePluralExamples';

describe('usePluralExamples', () => {
  beforeAll(() => {
    sinon.stub(console, 'error');
    sinon.stub(React, 'useMemo').callsFake((cb) => cb());
  });
  afterEach(() => console.error.resetHistory());
  afterAll(() => {
    console.error.restore();
    React.useMemo.restore();
  });

  it('returns a map of Slovenian plural examples', () => {
    const res = usePluralExamples({
      cldrPlurals: [1, 2, 3, 5],
      pluralRule:
        '(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3)',
    });

    expect(res).toEqual({ 1: 1, 2: 2, 3: 3, 5: 0 });
    expect(console.error.callCount).toBe(0);
  });

  it('prevents infinite loop if locale plurals are not configured properly', () => {
    const res = usePluralExamples({
      cldrPlurals: [0, 1, 2, 3, 4, 5],
      pluralRule: '(n != 1)',
    });

    expect(res).toEqual({ 0: 1, 1: 2 });
    expect(console.error.callCount).toBe(1);
  });
});
