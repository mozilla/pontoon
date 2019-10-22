import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import SourceString from './SourceString';


const ORIGINAL = 'title = Hello From The Other Side';

const ENTITY = {
    original: ORIGINAL,
};

describe('<SourceString>', () => {
    it('renders the original source input', () => {
        const wrapper = shallow(<SourceString
            entity = { ENTITY }
        />);

        expect(wrapper.find('SourceString')).toBeDefined();

        expect(wrapper.find('.original ContentMarker').children()).toHaveLength(1);
        expect(wrapper.find('.original ContentMarker').children().text()).toEqual('title = Hello From The Other Side');
    });

    it('calls the handleClickOnPlaceable function on click on .original', () => {
        const handleClickOnPlaceable = sinon.spy();
        const wrapper = shallow(<SourceString
            entity = { ENTITY }
            handleClickOnPlaceable={ handleClickOnPlaceable }
        />);

        wrapper.find('.original').simulate('click');
        expect(handleClickOnPlaceable.called).toEqual(true);
    });
});