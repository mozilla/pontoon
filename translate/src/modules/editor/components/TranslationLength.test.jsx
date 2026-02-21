import React, { useContext } from 'react';

import { EditorData, EditorResult } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';

import { TranslationLength } from './TranslationLength';
import { vi } from 'vitest';
import { render } from '@testing-library/react';

describe('<TranslationLength>', () => {
  beforeAll(() => {
    vi.mock('react', async (importOriginal) => {
      const actual = await importOriginal();
      return {
        ...actual,
        useContext: vi.fn(),
      };
    });
  });

  afterAll(() => {
    vi.restoreAllMocks();
  });

  function mountTranslationLength(format, original, value, comment) {
    const context = new Map([
      [EditorData, { sourceView: false }],
      [EditorResult, [{ value }]],
      [EntityView, { entity: { comment, format, original } }],
    ]);
    vi.mocked(useContext).mockImplementation((key) => context.get(key));

    return render(<TranslationLength />);
  }

  it('shows translation length and original string length', () => {
    const { container } = mountTranslationLength('', '12345', '1234567', '');

    const div = container.querySelector('.translation-vs-original');
    expect(div.childNodes[0].textContent).toEqual('7');
    expect(div.childNodes[1].textContent).toEqual('|');
    expect(div.childNodes[2].textContent).toEqual('5');
  });

  it('shows translation length and plural original string length', () => {
    const { container } = mountTranslationLength('', '123456', '1234567', '');

    const div = container.querySelector('.translation-vs-original');
    expect(div.childNodes[2].textContent).toEqual('6');
  });

  it('shows translation length and FTL original string length', () => {
    const { container } = mountTranslationLength(
      'fluent',
      'key = 123456',
      '1234567',
      '',
    );

    const div = container.querySelector('.translation-vs-original');
    expect(div.childNodes[0].textContent).toEqual('7');
    expect(div.childNodes[2].textContent).toEqual('6');
  });

  it('does not strip html from translation when calculating length', () => {
    const { container } = mountTranslationLength(
      '',
      '12345',
      '12<span>34</span>56',
      '',
    );

    const div = container.querySelector('.translation-vs-original');
    expect(div.childNodes[0].textContent).toEqual('19');
  });
});
