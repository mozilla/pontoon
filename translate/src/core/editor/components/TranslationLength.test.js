import React from 'react';
import { shallow } from 'enzyme';

import { EditorData } from '~/context/Editor';
import { PluralForm } from '~/context/PluralForm';
import * as SelectedEntity from '~/core/entities/hooks';

import { TranslationLength } from './TranslationLength';
import sinon from 'sinon';

describe('<TranslationLength>', () => {
  beforeAll(() => {
    sinon.stub(React, 'useContext'); //.callsFake(({ children }) => children);
    sinon.stub(SelectedEntity, 'useSelectedEntity');
  });

  afterAll(() => {
    React.useContext.restore();
    SelectedEntity.useSelectedEntity.restore();
  });

  function mountTranslationLength(format, original, value, comment) {
    const context = new Map([
      [EditorData, { value, view: 'simple' }],
      [PluralForm, { pluralForm: -1 }],
    ]);
    React.useContext.callsFake((key) => context.get(key));

    SelectedEntity.useSelectedEntity.returns({ comment, format, original });

    return shallow(<TranslationLength />);
  }

  it('shows translation length and original string length', () => {
    const wrapper = mountTranslationLength('', '12345', '1234567', '');

    expect(wrapper.find('.countdown')).toHaveLength(0);
    expect(wrapper.find('.translation-vs-original').childAt(0).text()).toEqual(
      '7',
    );
    expect(wrapper.find('.translation-vs-original').childAt(1).text()).toEqual(
      '|',
    );
    expect(wrapper.find('.translation-vs-original').childAt(2).text()).toEqual(
      '5',
    );
  });

  it('shows translation length and plural original string length', () => {
    const wrapper = mountTranslationLength('', '123456', '1234567', '');

    expect(wrapper.find('.translation-vs-original').childAt(2).text()).toEqual(
      '6',
    );
  });

  it('shows countdown if MAX_LENGTH provided in LANG entity comment', () => {
    const wrapper = mountTranslationLength(
      'lang',
      '12345',
      '123',
      'MAX_LENGTH: 5\nThis is an actual comment.',
    );

    expect(wrapper.find('.translation-vs-original')).toHaveLength(0);
    expect(wrapper.find('.countdown span').text()).toEqual('2');
    expect(wrapper.find('.countdown span.overflow')).toHaveLength(0);
  });

  it('marks countdown overflow', () => {
    const wrapper = mountTranslationLength(
      'lang',
      '12345',
      '123456',
      'MAX_LENGTH: 5\nThis is an actual comment.',
    );

    expect(wrapper.find('.countdown span.overflow')).toHaveLength(1);
  });

  it('strips html from translation when calculating countdown', () => {
    const wrapper = mountTranslationLength(
      'lang',
      '12345',
      '12<span>34</span>56',
      'MAX_LENGTH: 5\nThis is an actual comment.',
    );

    expect(wrapper.find('.countdown span').text()).toEqual('-1');
  });

  it('does not strips html from translation when calculating length', () => {
    const wrapper = mountTranslationLength(
      '',
      '12345',
      '12<span>34</span>56',
      '',
    );

    expect(wrapper.find('.translation-vs-original').childAt(0).text()).toEqual(
      '19',
    );
  });
});
