import React from 'react';

import { TranslationDiff } from './TranslationDiff';
import { render } from '@testing-library/react';

describe('<TranslationDiff>', () => {
  it('returns the correct diff for provided strings', () => {
    const { getByText, container } = render(
      <TranslationDiff base={'abcdef'} target={'cdefgh'} />,
    );

    getByText('gh', { selector: 'ins' });
    getByText('ab', { selector: 'del' });
    expect(container.childNodes[1]).toHaveTextContent(/^cdef$/);
  });

  it('returns the same string if provided strings are equal', () => {
    const { container } = render(
      <TranslationDiff base={'abcdef'} target={'abcdef'} />,
    );

    expect(container.querySelector('ins')).toBeNull();
    expect(container.querySelector('del')).toBeNull();
    expect(container).toHaveTextContent(/^abcdef$/);
  });
});
