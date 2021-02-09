import React from 'react';
import { shallow } from 'enzyme';

import CaighdeanTranslation from './CaighdeanTranslation';

describe('<CaighdeanTranslation>', () => {
    it('renders the CaighdeanTranslation component properly', () => {
        const wrapper = shallow(<CaighdeanTranslation />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual(
            'machinery-CaighdeanTranslation--visit-caighdean',
        );
        expect(wrapper.find('li a').props().href).toEqual(
            'https://github.com/kscanne/caighdean',
        );
        expect(wrapper.find('li a').props().title).toEqual(
            'Visit Caighdean Machine Translation',
        );
        expect(wrapper.find('li a span').text()).toEqual('CAIGHDEAN');
    });
});
