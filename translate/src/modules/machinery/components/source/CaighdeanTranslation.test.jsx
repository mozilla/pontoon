import React from 'react';
import { shallow } from 'enzyme';

import { CaighdeanTranslation } from './CaighdeanTranslation';

describe('<CaighdeanTranslation>', () => {
  it('renders the CaighdeanTranslation component properly', () => {
    const wrapper = shallow(<CaighdeanTranslation />);

    expect(wrapper.find('li')).toHaveLength(1);
    expect(wrapper.find('Localized').props().id).toEqual(
      'machinery-CaighdeanTranslation--translation-source',
    );
    expect(wrapper.find('li span').text()).toEqual('CAIGHDEAN');
  });
});
