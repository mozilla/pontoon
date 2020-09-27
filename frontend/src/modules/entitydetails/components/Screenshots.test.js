import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import Screenshots from './Screenshots';

function createShallowScreenshots(source, openLightboxFake = null) {
    return shallow(
        <Screenshots
            source={source}
            locale='kg'
            openLightbox={openLightboxFake}
        />,
    );
}

describe('<Screenshots>', () => {
    it('renders an image when there is an image URL in the source', () => {
        const source = 'That is an image URL: http://link.to/image.png';
        const wrapper = createShallowScreenshots(source);

        const images = wrapper.find('img');
        expect(images).toHaveLength(1);
        expect(images.props().src).toEqual('http://link.to/image.png');
    });

    it('can render several images', () => {
        const source = `
            Here we have 2 images: http://link.to/image.png
            and https://example.org/test.jpg
        `;
        const wrapper = createShallowScreenshots(source);

        const expectedImages = [
            'http://link.to/image.png',
            'https://example.org/test.jpg',
        ];

        const images = wrapper.find('img');
        expect(images).toHaveLength(2);
        images.forEach((node) => {
            expect(node.props().src).toEqual(expectedImages.shift());
        });
    });

    it('does not render non PNG or JPG images', () => {
        const source =
            'That is a non-supported image URL: http://link.to/image.bmp';
        const wrapper = createShallowScreenshots(source);

        expect(wrapper.find('img')).toHaveLength(0);
    });

    it('does not render non image links', () => {
        const source = 'That is not an image URL: http://link.to/image.php';
        const wrapper = createShallowScreenshots(source);

        expect(wrapper.find('img')).toHaveLength(0);
    });

    it('shows a Lightbox on image click', () => {
        const source = 'That is an image URL: http://link.to/image.png';
        const openLightboxFake = sinon.fake();
        const wrapper = createShallowScreenshots(source, openLightboxFake);

        wrapper.find('img').simulate('click');

        expect(openLightboxFake.calledOnce).toEqual(true);
    });
});
