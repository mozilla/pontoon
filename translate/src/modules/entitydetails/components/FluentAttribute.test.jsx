import ftl from '@fluent/dedent';
import React from 'react';
import { parseEntry } from '~/utils/message';
import { FluentAttribute } from './FluentAttribute';
import { render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

describe('isSimpleSingleAttributeMessage', () => {
  it('renders nonempty for a string with a single attribute', () => {
    const original = ftl`
      my-entry =
          .an-atribute = Hello!
      `;
    const entry = parseEntry('fluent', original);
    const { container } = render(
      <MockLocalizationProvider>
        <FluentAttribute entry={entry} />
      </MockLocalizationProvider>,
    );
    expect(container).not.toBeEmptyDOMElement();
  });

  it('renders null for string with value', () => {
    const original = ftl`
      my-entry = Something
          .an-atribute = Hello!
      `;
    const entry = parseEntry('fluent', original);
    const { container } = render(<FluentAttribute entry={entry} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders null for string with several attributes', () => {
    const original = ftl`
      my-entry =
          .an-atribute = Hello!
          .two-attrites = World!
      `;
    const entry = parseEntry('fluent', original);
    const { container } = render(<FluentAttribute entry={entry} />);
    expect(container).toBeEmptyDOMElement();
  });
});
