import React from 'react';
import { shallow } from 'enzyme';

import { EditorData, EditorResult } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';

import { TranslationLength } from './TranslationLength';
import sinon from 'sinon';

describe('<TranslationLength>', () => {
  beforeAll(() => {
    sinon.stub(React, 'useContext');
  });

  afterAll(() => {
    React.useContext.restore();
  });

  function mountTranslationLength(format, original, value, comment) {
    const context = new Map([
      [EditorData, { sourceView: false }],
      [EditorResult, [{ value }]],
      [EntityView, { entity: { comment, format, original }, pluralForm: 0 }],
    ]);
    React.useContext.callsFake((key) => context.get(key));

    return shallow(<TranslationLength />);
  }

  it('shows translation length and original string length', () => {
    const wrapper = mountTranslationLength('', '12345', '1234567', '');

    const div = wrapper.find('.translation-vs-original');
    expect(div.childAt(0).text()).toEqual('7');
    expect(div.childAt(1).text()).toEqual('|');
    expect(div.childAt(2).text()).toEqual('5');
  });

  it('shows translation length and plural original string length', () => {
    const wrapper = mountTranslationLength('', '123456', '1234567', '');

    const div = wrapper.find('.translation-vs-original');
    expect(div.childAt(2).text()).toEqual('6');
  });

  it('shows translation length and FTL original string length', () => {
    const wrapper = mountTranslationLength(
      'ftl',
      'key = 123456',
      '1234567',
      '',
    );

    const div = wrapper.find('.translation-vs-original');
    expect(div.childAt(0).text()).toEqual('7');
    expect(div.childAt(2).text()).toEqual('6');
  });

  it('does not strip html from translation when calculating length', () => {
    const wrapper = mountTranslationLength(
      '',
      '12345',
      '12<span>34</span>56',
      '',
    );

    const div = wrapper.find('.translation-vs-original');
    expect(div.childAt(0).text()).toEqual('19');
  });
});
