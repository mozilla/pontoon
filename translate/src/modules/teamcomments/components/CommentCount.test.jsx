import React from 'react';

import { CommentCount } from './CommentCount';
import { render } from '@testing-library/react';

describe('<CommentCount>', () => {
  it('shows the correct number of pinned comments', () => {
    const teamComments = {
      comments: [
        {
          pinned: true,
        },
        {
          pinned: true,
        },
      ],
    };
    const { container } = render(<CommentCount teamComments={teamComments} />);

    // There are only pinned results.
    expect(container.querySelectorAll('.count > span')).toHaveLength(1);

    // And there are two of them.
    expect(container.querySelector('.pinned')).toHaveTextContent('2');

    expect(container).not.toHaveTextContent('+');
  });

  it('shows the correct number of remaining comments', () => {
    const teamComments = {
      comments: [{}, {}, {}],
    };
    const { container } = render(<CommentCount teamComments={teamComments} />);

    // There are only remaining results.
    expect(container.querySelectorAll('.count > span')).toHaveLength(1);
    expect(container.querySelector('.pinned')).toBeNull();

    // And there are three of them.
    expect(container.querySelector('.count > span')).toHaveTextContent('3');

    expect(container).not.toHaveTextContent('+');
  });

  it('shows the correct numbers of pinned and remaining comments', () => {
    const teamComments = {
      comments: [
        {
          pinned: true,
        },
        {
          pinned: true,
        },
        {},
        {},
        {},
      ],
    };
    const { container } = render(<CommentCount teamComments={teamComments} />);

    const spans = container.querySelectorAll('.count > span');
    // There are both pinned and remaining, and the '+' sign.
    expect(spans).toHaveLength(3);

    // And each count is correct.
    expect(container.querySelector('.pinned')).toHaveTextContent('2');
    expect(spans[spans.length - 1]).toHaveTextContent('3');

    // And the final display is correct as well.
    expect(container).toHaveTextContent('2+3');
  });
});
