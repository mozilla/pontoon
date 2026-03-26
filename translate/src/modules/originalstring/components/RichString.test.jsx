import ftl from '@fluent/dedent';
import React from 'react';

import { editMessageEntry, parseEntry } from '~/utils/message';
import { RichString } from './RichString';
import { fireEvent, render } from '@testing-library/react';

const ORIGINAL = ftl`
  song-title = Hello
      .genre = Pop
      .album = Hello and Good Bye
  `;

describe('<RichString>', () => {
  it('renders value and each attribute correctly', () => {
    const message = editMessageEntry(parseEntry('fluent', ORIGINAL));
    const { container } = render(<RichString message={message} terms={{}} />);

    const labels = container.querySelectorAll('label');
    const highlights = container.querySelectorAll('td > span');

    expect(highlights).toHaveLength(3);

    expect(labels[0]).toHaveTextContent('Value');
    expect(highlights[0]).toHaveTextContent('Hello');

    expect(labels[1]).toHaveTextContent('genre');
    expect(highlights[1]).toHaveTextContent('Pop');

    expect(labels[2]).toHaveTextContent('album');
    expect(highlights[2]).toHaveTextContent('Hello and Good Bye');
  });

  it('renders select expression correctly', () => {
    const input = ftl`
      user-entry =
          { PLATFORM() ->
              [variant-1] Hello!
             *[variant-2] Good Bye!
          }
      `;

    const message = editMessageEntry(parseEntry('fluent', input));
    const { container } = render(<RichString message={message} terms={{}} />);
    const labels = container.querySelectorAll('label');
    const highlights = container.querySelectorAll('td > span');

    expect(labels[0]).toHaveTextContent('variant-1');
    expect(highlights[0]).toHaveTextContent('Hello!');

    expect(labels[1]).toHaveTextContent('variant-2');
    expect(highlights[1]).toHaveTextContent('Good Bye!');
  });

  it('renders select expression in attributes properly', () => {
    const input = ftl`
      my-entry =
          .label =
              { PLATFORM() ->
                  [macosx] Preferences
                 *[other] Options
              }
          .accesskey =
              { PLATFORM() ->
                  [macosx] e
                 *[other] s
              }
      `;

    const message = editMessageEntry(parseEntry('fluent', input));
    const { container } = render(<RichString message={message} terms={{}} />);

    const labels = container.querySelectorAll('label');
    const highlights = container.querySelectorAll('td > span');

    expect(labels).toHaveLength(4);
    expect(highlights).toHaveLength(4);

    expect(labels[0]).toHaveTextContent(/label.*macosx/);
    expect(highlights[0]).toHaveTextContent('Preferences');

    expect(labels[1]).toHaveTextContent(/label.*other/);
    expect(highlights[1]).toHaveTextContent('Options');

    expect(labels[2]).toHaveTextContent(/accesskey.*macosx/);
    expect(labels[2]).toHaveTextContent('e');

    expect(labels[3]).toHaveTextContent(/accesskey.*other/);
    expect(labels[3]).toHaveTextContent('s');
  });

  it('calls the onClick function on click on .original', () => {
    const message = editMessageEntry(parseEntry('fluent', ORIGINAL));
    const spy = vi.fn();
    const { container } = render(
      <RichString message={message} onClick={spy} terms={{}} />,
    );
    fireEvent.click(container.querySelector('.original'));
    expect(spy).toHaveBeenCalled();
  });
});
