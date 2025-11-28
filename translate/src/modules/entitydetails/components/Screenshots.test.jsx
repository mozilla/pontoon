import React from 'react';
import { act } from 'react-dom/test-utils';
import { Screenshots } from './Screenshots';
import { mount } from 'enzyme';

describe('<Screenshots>', () => {
  it('finds several images', () => {
    const source = `
      Here we have 2 images: http://link.to/image.png
      and https://example.org/en-US/test.jpg
    `;
    const wrapper = mount(<Screenshots locale='kg' source={source} />);

    expect(wrapper.find('img')).toHaveLength(2);
    expect(wrapper.find('img').at(0).prop('src')).toBe(
      'http://link.to/image.png',
    );
    expect(wrapper.find('img').at(1).prop('src')).toBe(
      'https://example.org/kg/test.jpg',
    );
  });

  it('does not find non PNG or JPG images', () => {
    const source =
      'That is a non-supported image URL: http://link.to/image.bmp';
    const wrapper = mount(<Screenshots locale='kg' source={source} />);

    expect(wrapper.find('img')).toHaveLength(0);
  });

  it('shows a Lightbox on image click', () => {
    const source = 'That is an image URL: http://link.to/image.png';
    const wrapper = mount(<Screenshots locale='kg' source={source} />);

    expect(wrapper.find('.lightbox')).toHaveLength(0);

    wrapper.find('img').simulate('click');

    expect(wrapper.find('.lightbox')).toHaveLength(1);
  });

  it('Lightbox closes on click', () => {
    const source = 'That is an image URL: http://link.to/image.png';
    const wrapper = mount(<Screenshots locale='kg' source={source} />);
    wrapper.find('img').simulate('click');
    wrapper.find('.lightbox').simulate('click');

    expect(wrapper.find('.lightbox')).toHaveLength(0);
  });

  it('Lightbox closes on key press', () => {
    const source = 'That is an image URL: http://link.to/image.png';
    const wrapper = mount(<Screenshots locale='kg' source={source} />);
    wrapper.find('img').simulate('click');
    act(() => {
      window.document.dispatchEvent(
        new KeyboardEvent('keydown', { code: 'Escape' }),
      );
    });
    wrapper.update();

    expect(wrapper.find('.lightbox')).toHaveLength(0);
  });
});
