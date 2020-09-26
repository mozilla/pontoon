import React from 'react';
import { shallow } from 'enzyme';

import Count from './Count';

describe('<Count>', () => {
    it('shows the correct number of preferred translations', () => {
        const machinery = {
            translations: [
                { sources: ['translation-memory'] },
                { sources: ['translation-memory'] },
            ],
        };
        const wrapper = shallow(<Count machinery={machinery} />);

        // There are only preferred results.
        expect(wrapper.find('.count > span')).toHaveLength(1);

        // And there are two of them.
        expect(wrapper.find('.preferred').text()).toContain('2');

        expect(wrapper.text()).not.toContain('+');
    });

    it('shows the correct number of remaining translations', () => {
        const machinery = {
            translations: [
                { sources: ['microsoft'] },
                { sources: ['transvision'] },
                { sources: ['transvision'] },
            ],
        };
        const wrapper = shallow(<Count machinery={machinery} />);

        // There are only remaining results.
        expect(wrapper.find('.count > span')).toHaveLength(1);
        expect(wrapper.find('.preferred')).toHaveLength(0);

        // And there are three of them.
        expect(wrapper.find('.count > span').text()).toContain('3');

        expect(wrapper.text()).not.toContain('+');
    });

    it('shows the correct numbers of preferred and remaining translations', () => {
        const machinery = {
            translations: [
                { sources: ['translation-memory'] },
                { sources: ['translation-memory'] },
                { sources: ['microsoft'] },
                { sources: ['transvision'] },
                { sources: ['transvision'] },
            ],
        };
        const wrapper = shallow(<Count machinery={machinery} />);

        // There are both preferred and remaining, and the '+' sign.
        expect(wrapper.find('.count > span')).toHaveLength(3);

        // And each count is correct.
        expect(wrapper.find('.preferred').text()).toContain('2');
        expect(wrapper.find('.count > span').last().text()).toContain('3');

        // And the final display is correct as well.
        expect(wrapper.text()).toEqual('2+3');
    });
});
