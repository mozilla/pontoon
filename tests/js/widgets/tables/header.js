
import React from 'react';

import {shallow} from 'enzyme';

import {TableHeader} from 'widgets/tables';


test('TableHeader render', () => {
    const header = shallow(<TableHeader foo={7} bar={23}>HEADER</TableHeader>);

    expect(header.text()).toBe('HEADER');
    expect(header.props()).toEqual(
        {children: ['HEADER', <i className="fa" />],
         className: undefined,
         id: undefined});
});
