import React from 'react';
import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { EditorData, EditorResult } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { MockLocalizationProvider } from '~/test/utils';
import { parseEntry } from '~/utils/message';
import { addRtlMarks } from '~/utils/message/rtlMark';

import { RtlMarkIndicator } from './RtlMarkIndicator';

const field = (value) => ({ handle: { current: { value } } });

const mount = ({
  direction = 'rtl',
  values = ['{ $name } را باز کنید'],
  sourceView = false,
  result = null,
}) =>
  render(
    <MockLocalizationProvider
      resources={[
        `editor-RtlMarkIndicator--rlm = RLM
    .title = A right-to-left mark (RLM) will be added`,
      ]}
    >
      <Locale.Provider value={{ direction }}>
        <EditorData.Provider value={{ fields: values.map(field), sourceView }}>
          <EditorResult.Provider value={result}>
            <RtlMarkIndicator />
          </EditorResult.Provider>
        </EditorData.Provider>
      </Locale.Provider>
    </MockLocalizationProvider>,
  );

describe('<RtlMarkIndicator>', () => {
  it('shows when an RTL translation starts with LTR content', () => {
    const { container } = mount({});

    const indicator = container.querySelector('.rtl-mark');
    expect(indicator).not.toBeNull();
    expect(indicator.textContent).toBe('RLM');
    expect(indicator.getAttribute('title')).toBeTruthy();
  });

  it('shows when any of the fields needs a mark', () => {
    const { container } = mount({ values: ['فایل', 'Firefox فایل'] });

    expect(container.querySelector('.rtl-mark')).not.toBeNull();
  });

  it('shows nothing for content starting with RTL text', () => {
    const { container } = mount({ values: ['فایرفاکس را باز کنید'] });

    expect(container.querySelector('.rtl-mark')).toBeNull();
  });

  it('shows nothing for unchanged translations', () => {
    const result = parseEntry('fluent', 'key = { $n } فایل');
    const { container } = render(
      <MockLocalizationProvider>
        <Locale.Provider value={{ direction: 'rtl' }}>
          <EditorData.Provider
            value={{
              fields: [field('{ $n } فایل')],
              initial: result,
              sourceView: false,
            }}
          >
            <EditorResult.Provider value={result}>
              <RtlMarkIndicator />
            </EditorResult.Provider>
          </EditorData.Provider>
        </Locale.Provider>
      </MockLocalizationProvider>,
    );

    expect(container.querySelector('.rtl-mark')).toBeNull();
  });

  it('shows nothing for LTR locales', () => {
    const { container } = mount({ direction: 'ltr' });

    expect(container.querySelector('.rtl-mark')).toBeNull();
  });

  it('shows in the source view when the result gets a mark', () => {
    const result = addRtlMarks(parseEntry('fluent', 'key = { $n } فایل'));
    const { container } = mount({ sourceView: true, result });

    expect(container.querySelector('.rtl-mark')).not.toBeNull();
  });

  it('shows nothing in the source view without a mark', () => {
    const result = parseEntry('fluent', 'key = فایل { $n }');
    const { container } = mount({ sourceView: true, result });

    expect(container.querySelector('.rtl-mark')).toBeNull();
  });
});
