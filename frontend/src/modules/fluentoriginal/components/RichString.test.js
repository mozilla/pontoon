import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import RichString from './RichString';


const ORIGINAL = 'song-title = Hello\n    .genre = Pop\n    .album = Hello and Good Bye';

const ENTITY = {
    original: ORIGINAL,
};

describe('<RichString>', () => {
    it('renders correct value and each attribute of original input', () => {
        const wrapper = shallow(<RichString
            entity = { ENTITY }
        />);

        expect(wrapper.find('RichString')).toBeDefined();

        expect(wrapper.find('ContentMarker')).toHaveLength(3);
        expect(wrapper.find('ContentMarker').at(0).html()).toContain('Hello');
        expect(wrapper.find('ContentMarker').at(1).html()).toContain('Pop');
        expect(wrapper.find('ContentMarker').at(2).html()).toContain('Hello and Good Bye');
    });

    it('renders select expression correctly', () => {
        const input = `
user-entry =
    { PLATFORM() ->
        [variant-1] Hello!
       *[variant-2] Good Bye!
    }`;

        const entity = {
            original: input,
        };

        const wrapper = shallow(<RichString
            entity = { entity }
        />);

        expect(wrapper.find('ContentMarker')).toHaveLength(2);

        expect(wrapper.find('label').at(0).html()).toContain('variant-1');
        expect(wrapper.find('ContentMarker').at(0).html()).toContain('Hello!');

        expect(wrapper.find('label').at(1).html()).toContain('variant-2');
        expect(wrapper.find('ContentMarker').at(1).html()).toContain('Good Bye!');
    });

    it('calls the handleClickOnPlaceable function on click on .original', () => {
        const handleClickOnPlaceable = sinon.spy();
        const wrapper = shallow(<RichString
            entity = { ENTITY }
            handleClickOnPlaceable={ handleClickOnPlaceable }
        />);

        wrapper.find('.original').simulate('click');
        expect(handleClickOnPlaceable.called).toEqual(true);
    });
});