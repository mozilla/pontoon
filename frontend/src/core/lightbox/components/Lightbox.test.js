import React from 'react';
import { mount } from 'enzyme';
import sinon from 'sinon';

import Lightbox from './Lightbox';


describe('<Lightbox>', () => {
    it('renders the image correctly', () => {
        const wrapper = mount(
            <Lightbox image="http://example.org/empty.png" close={ null } />
        );

        expect(wrapper.find('img')).toHaveLength(1);
        expect(wrapper.find('img').props().src).toEqual("http://example.org/empty.png");
    });

    it('closes on click', () => {
        const closeFn = sinon.spy();
        const wrapper = mount(
            <Lightbox image="http://example.org/empty.png" close={ closeFn } />
        );

        wrapper.simulate('click');
        expect(closeFn.calledOnce).toEqual(true);

        wrapper.simulate('click');
        expect(closeFn.callCount).toEqual(2);
    });

    it('closes on key presses', () => {
        // Simulating the key presses on `document`.
        // See https://github.com/airbnb/enzyme/issues/426
        const eventsMap = {};
        document.addEventListener = sinon.spy((event, cb) => {
            eventsMap[event] = cb;
        });

        const closeFn = sinon.spy();
        mount(
            <Lightbox image="http://example.org/empty.png" close={ closeFn } />
        );

        eventsMap.keydown({keyCode: 13});
        expect(closeFn.callCount).toEqual(1);

        eventsMap.keydown({keyCode: 27});
        expect(closeFn.callCount).toEqual(2);

        eventsMap.keydown({keyCode: 32});
        expect(closeFn.callCount).toEqual(3);
    });
});
