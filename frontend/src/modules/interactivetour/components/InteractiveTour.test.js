import React from 'react';
import Tour from 'reactour';
import { shallow } from 'enzyme';

import { InteractiveTourBase } from './InteractiveTour';

describe('<InteractiveTourBase>', () => {
    it('renders correctly on the tutorial page for unauthenticated user', () => {
        const wrapper = shallow(
            <InteractiveTourBase
                locale={{ code: 'lc' }}
                project={{ slug: 'tutorial' }}
                user={{ isAuthenticated: false }}
            />,
        );

        expect(wrapper.find(Tour)).toHaveLength(1);
    });

    it('does not render on non-tutorial page', () => {
        const wrapper = shallow(
            <InteractiveTourBase
                locale={{ code: 'lc' }}
                project={{ slug: 'firefox' }}
                user={{ isAuthenticated: false }}
            />,
        );

        expect(wrapper.find(Tour)).toHaveLength(0);
    });

    it('does not render if the user has already seen the tutorial', () => {
        const wrapper = shallow(
            <InteractiveTourBase
                locale={{ code: 'lc' }}
                project={{ slug: 'tutorial' }}
                // the user has seen the tutorial
                user={{ tourStatus: -1 }}
            />,
        );

        expect(wrapper.find(Tour)).toHaveLength(0);
    });
});
