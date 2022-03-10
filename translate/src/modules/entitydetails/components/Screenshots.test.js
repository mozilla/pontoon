import React from 'react';
import { act } from 'react-dom/test-utils';
import Screenshots from './Screenshots';
import { mount } from 'enzyme';

describe('<Screenshots>', () => {
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
