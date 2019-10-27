import React from 'react';
import { shallow } from 'enzyme';

import CaighdeanTranslation from './CaighdeanTranslation';


describe('<CaighdeanTranslation>', () => {
    it('renders the component properly', () => {
        const source = {
            type: 'caighdean',
            url: 'https://github.com/kscanne/caighdean',
            id: 'machinery-CaighdeanTranslation--visit-caighdean',
            string: 'Caighdean',
            title: 'Visit Caighdean Machine Translation',
        };

        const wrapper = shallow(<CaighdeanTranslation
            source={ source }
        />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('Localized').props().id).toEqual(source.id);
        expect(wrapper.find('li a').props().href).toEqual(source.url);
        expect(wrapper.find('li a').props().title).toEqual(source.title);
        expect(wrapper.find('li a span').text()).toEqual(source.string);
    });
});
