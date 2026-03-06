import React from 'react';
import { act } from 'react-dom/test-utils';
import { Screenshots } from './Screenshots';
import { fireEvent, render } from '@testing-library/react';
import { expect } from 'vitest';

// TODO: Replace the querySelector with testing-library-ish approaches
describe('<Screenshots>', () => {
  it('finds several images', () => {
    const source = `
      Here we have 2 images: http://link.to/image.png
      and https://example.org/en-US/test.jpg
    `;
    const { getAllByRole } = render(
      <Screenshots locale='kg' source={source} />,
    );
    const images = getAllByRole('img');
    expect(images).toHaveLength(2);
    expect(images[0]).toHaveAttribute('src', 'http://link.to/image.png');
    expect(images[1]).toHaveAttribute('src', 'https://example.org/kg/test.jpg');
  });

  it('does not find non PNG or JPG images', () => {
    const source =
      'That is a non-supported image URL: http://link.to/image.bmp';
    const { queryByRole } = render(<Screenshots locale='kg' source={source} />);

    expect(queryByRole('img')).toBeNull();
  });

  it('shows a Lightbox on image click', () => {
    const source = 'That is an image URL: http://link.to/image.png';
    const { container, getByRole } = render(
      <Screenshots locale='kg' source={source} />,
    );

    expect(container.querySelector('.lightbox')).toBeNull();
    fireEvent.click(getByRole('img'));

    expect(container.querySelector('.lightbox')).toBeInTheDocument();
  });

  it('Lightbox closes on click', () => {
    const source = 'That is an image URL: http://link.to/image.png';
    const { getByRole, container } = render(
      <Screenshots locale='kg' source={source} />,
    );
    fireEvent.click(getByRole('img'));
    fireEvent.click(container.querySelector('.lightbox'));

    expect(container.querySelector('.lightbox')).toBeNull();
  });

  it('Lightbox closes on key press', () => {
    const source = 'That is an image URL: http://link.to/image.png';
    const { getByRole, container } = render(
      <Screenshots locale='kg' source={source} />,
    );
    fireEvent.click(getByRole('img'));
    act(() => {
      window.document.dispatchEvent(
        new KeyboardEvent('keydown', { code: 'Escape' }),
      );
    });

    expect(container.querySelector('.lightbox')).toBeNull();
  });
});
