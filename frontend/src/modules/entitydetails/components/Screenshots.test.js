import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import Screenshots from './Screenshots';

describe('<Screenshots>', () => {
    it('shows a Lightbox on image click', () => {
        const source = 'That is an image URL: http://link.to/image.png';
        const openLightboxFake = sinon.fake();
        const wrapper = shallow(
            <Screenshots
                source={source}
                locale='kg'
                openLightbox={openLightboxFake}
            />,
        );

        wrapper.find('img').simulate('click');

        expect(openLightboxFake.calledOnce).toEqual(true);
    });
});
