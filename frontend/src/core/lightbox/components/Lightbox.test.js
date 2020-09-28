import React from 'react';
import { act } from 'react-dom/test-utils';
import { shallow, mount } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';

import * as actions from '../actions';
import Lightbox, { LightboxBase } from './Lightbox';

describe('<LightboxBase>', () => {
    it('renders the image correctly', () => {
        const state = {
            image: 'http://example.org/empty.png',
            isOpen: true,
        };
        const wrapper = shallow(<LightboxBase lightbox={state} />);

        expect(wrapper.find('img')).toHaveLength(1);
        expect(wrapper.find('img').props().src).toEqual(
            'http://example.org/empty.png',
        );
    });
});

describe('<Lightbox>', () => {
    it('is hidden by default', () => {
        const store = createReduxStore();
        const wrapper = mount(<Lightbox store={store} />);

        expect(wrapper.find('img')).toHaveLength(0);
    });

    it('hides after the close action is called', () => {
        const store = createReduxStore();
        store.dispatch(actions.open('http://example.org/empty.png'));

        const wrapper = mount(<Lightbox store={store} />);
        expect(wrapper.find('img')).toHaveLength(1);

        act(() => {
            store.dispatch(actions.close());
        });
        expect(wrapper.update().find('img')).toHaveLength(0);
    });
});

describe('<LightboxEvents>', () => {
    beforeAll(() => {
        const closeMock = sinon.stub(actions, 'close');
        closeMock.returns({ type: 'whatever' });
    });

    afterEach(() => {
        // Make sure tests do not pollute one another.
        actions.close.resetHistory();
    });

    afterAll(() => {
        actions.close.restore();
    });

    it('closes on click', () => {
        const store = createReduxStore();
        store.dispatch(actions.open('http://example.org/empty.png'));

        const wrapper = mount(<Lightbox store={store} />);

        expect(wrapper.update().find('img')).toHaveLength(1);
        wrapper.simulate('click');
        expect(actions.close.calledOnce).toEqual(true);
    });

    it('closes on key presses', () => {
        const store = createReduxStore();

        // Simulating the key presses on `document`.
        // See https://github.com/airbnb/enzyme/issues/426
        const eventsMap = {};
        document.addEventListener = sinon.spy((event, cb) => {
            eventsMap[event] = cb;
        });

        mount(<Lightbox store={store} />);

        eventsMap.keydown({ keyCode: 13 });
        expect(actions.close.callCount).toEqual(1);

        eventsMap.keydown({ keyCode: 27 });
        expect(actions.close.callCount).toEqual(2);

        eventsMap.keydown({ keyCode: 32 });
        expect(actions.close.callCount).toEqual(3);
    });
});
