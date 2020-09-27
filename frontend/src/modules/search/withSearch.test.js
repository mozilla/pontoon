import React from 'react';
import { shallow } from 'enzyme';

import { markSearchTerms } from './withSearch';

describe('markSearchTerms', () => {
    it('does not break on regexp special characters', () => {
        const marked = markSearchTerms('foo (bar)', '(bar');
        const wrapper = shallow(<p>{marked}</p>);
        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toEqual('(bar');
    });
});
