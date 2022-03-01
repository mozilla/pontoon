import React from 'react';
import { shallow } from 'enzyme';

import ProjectPercent from './ProjectPercent';

describe('<ProjectPercent>', () => {
    const LOCALIZATION = {
        approvedStrings: 2,
        stringsWithWarnings: 3,
        totalStrings: 10,
    };

    it('renders correctly', () => {
        const wrapper = shallow(<ProjectPercent localization={LOCALIZATION} />);
        expect(wrapper.find('.percent').text()).toEqual('50%');
    });
});
