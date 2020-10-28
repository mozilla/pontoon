import React from 'react';
import { shallow } from 'enzyme';

import Count from './Count';

describe('<Count>', () => {
    it('shows the correct number of pinned comments', () => {
        const teamComments = {
            comments: [
                {
                    pinned: true,
                },
                {
                    pinned: true,
                },
            ],
        };
        const wrapper = shallow(<Count teamComments={teamComments} />);

        // There are only pinned results.
        expect(wrapper.find('.count > span')).toHaveLength(1);

        // And there are two of them.
        expect(wrapper.find('.pinned').text()).toContain('2');

        expect(wrapper.text()).not.toContain('+');
    });

    it('shows the correct number of remaining comments', () => {
        const teamComments = {
            comments: [{}, {}, {}],
        };
        const wrapper = shallow(<Count teamComments={teamComments} />);

        // There are only remaining results.
        expect(wrapper.find('.count > span')).toHaveLength(1);
        expect(wrapper.find('.pinned')).toHaveLength(0);

        // And there are three of them.
        expect(wrapper.find('.count > span').text()).toContain('3');

        expect(wrapper.text()).not.toContain('+');
    });

    it('shows the correct numbers of pinned and remaining comments', () => {
        const teamComments = {
            comments: [
                {
                    pinned: true,
                },
                {
                    pinned: true,
                },
                {},
                {},
                {},
            ],
        };
        const wrapper = shallow(<Count teamComments={teamComments} />);

        // There are both pinned and remaining, and the '+' sign.
        expect(wrapper.find('.count > span')).toHaveLength(3);

        // And each count is correct.
        expect(wrapper.find('.pinned').text()).toContain('2');
        expect(wrapper.find('.count > span').last().text()).toContain('3');

        // And the final display is correct as well.
        expect(wrapper.text()).toEqual('2+3');
    });
});
