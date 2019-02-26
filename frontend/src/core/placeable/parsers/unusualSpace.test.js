import React from 'react';
import { mount } from 'enzyme';

import createMarker from 'lib/react-content-marker';

import unusualSpace from './unusualSpace';


describe('unusualSpace', () => {
    it('marks a space at the beginning of a string', () => {
        const Marker = createMarker([unusualSpace]);
        const content = ' hello';

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(' ');
    });

    it('marks a space at the end of a string', () => {
        const Marker = createMarker([unusualSpace]);
        const content = 'hello ';

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(' ');
    });

    it('marks a space at the beginning of a line', () => {
        const Marker = createMarker([unusualSpace]);
        const content = 'hello,\n world';

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual(' ');
    });

    it('marks several spaces anywhere in a string', () => {
        const Marker = createMarker([unusualSpace]);
        const content = 'hello,  beautiful world'

        const wrapper = mount(<Marker>{ content }</Marker>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('  ');
    });
});
