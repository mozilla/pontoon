import React from 'react';

import { OtherLocalesCount } from './OtherLocalesCount';
import { render } from '@testing-library/react';

describe('<OtherLocalesCount>', () => {
  it('shows the correct number of preferred translations', () => {
    const otherlocales = {
      translations: [
        {
          locale: {
            code: 'ab',
          },
          is_preferred: true,
        },
        {
          locale: {
            code: 'cd',
          },
          is_preferred: true,
        },
      ],
    };
    const { container } = render(
      <OtherLocalesCount otherlocales={otherlocales} />,
    );

    // There are only preferred results.
    expect(container.querySelector('.count > span')).toBeInTheDocument();

    // And there are two of them.
    expect(container.querySelector('.preferred')).toHaveTextContent('2');

    expect(container).not.toHaveTextContent('+');
  });

  it('shows the correct number of other translations', () => {
    const otherlocales = {
      translations: [
        {
          locale: {
            code: 'ef',
          },
        },
        {
          locale: {
            code: 'gh',
          },
        },
        {
          locale: {
            code: 'ij',
          },
        },
      ],
    };
    const { container } = render(
      <OtherLocalesCount otherlocales={otherlocales} />,
    );

    // There are only remaining results.
    expect(container.querySelector('.count > span')).toBeInTheDocument();
    expect(container.querySelector('.preferred')).toBeNull();

    // And there are three of them.
    expect(container.querySelector('.count > span')).toHaveTextContent('3');

    expect(container).not.toHaveTextContent('+');
  });

  it('shows the correct numbers of preferred and other translations', () => {
    const otherlocales = {
      translations: [
        {
          locale: {
            code: 'ab',
          },
          is_preferred: true,
        },
        {
          locale: {
            code: 'cd',
          },
          is_preferred: true,
        },
        {
          locale: {
            code: 'ef',
          },
        },
        {
          locale: {
            code: 'gh',
          },
        },
        {
          locale: {
            code: 'ij',
          },
        },
      ],
    };
    const { container } = render(
      <OtherLocalesCount otherlocales={otherlocales} />,
    );

    // There are both preferred and remaining, and the '+' sign.
    expect(container.querySelectorAll('.count > span')).toHaveLength(3);

    // And each count is correct.
    expect(container.querySelector('.preferred')).toHaveTextContent('2');
    const spans = container.querySelectorAll('.count > span');
    expect(spans[spans.length - 1]).toHaveTextContent('3');

    // And the final display is correct as well.
    expect(container).toHaveTextContent('2+3');
  });
});
