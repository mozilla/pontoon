import React from 'react';

import { shallow } from 'enzyme';

import { ErrorList, Error } from 'widgets/errors';

test('Error render', () => {
    let error = shallow(<Error name='FOO' error='BAR' />);
    expect(error.text()).toBe('FOO: BAR');
    let li = error.find('li.error');
    expect(li.length).toBe(1);
});

test('ErrorList render', () => {
    let errors = shallow(<ErrorList errors={{}} />);
    expect(errors.text()).toBe('');
    expect(errors.find('ul').length).toBe(0);
    errors = shallow(
        <ErrorList errors={{ foo: 'Did a foo', bar: 'Bars happen' }} />,
    );
    let ul = errors.find('ul.errors');
    expect(ul.length).toBe(1);
    let lis = ul.find(Error);
    expect(lis.length).toBe(2);
    expect(errors.text()).toBe('<Error /><Error />');
});
