import { mount } from 'enzyme';
import React from 'react';

import { TagResourceSearch } from './search.js';

test('TagResourceSearch renders search input', () => {
    const search = mount(<TagResourceSearch />);
    const input = search.find('input.search-tag-resources');

    expect(input).toHaveLength(1);
    expect(input.html()).toMatch('placeholder="Search for resources"');
});

test('TagResourceSearch renders select', () => {
    const search = mount(<TagResourceSearch />);
    const options = search.find('select.search-tag-resource-type option');

    expect(options).toHaveLength(2);
    expect(options.at(0).html()).toMatch('"assoc"');
    expect(options.at(1).html()).toMatch('"nonassoc"');
});

test('TagResourceSearch onChange', async () => {
    const search = jest.fn();
    const type = jest.fn();
    const wrapper = mount(
        <TagResourceSearch onSearch={search} onType={type} />,
    );

    wrapper.find('input').simulate('change', { target: { value: 'FOO' } });
    wrapper.find('select').simulate('change', { target: { value: 'BAR' } });

    expect(search.mock.calls).toEqual([['FOO']]);
    expect(type.mock.calls).toEqual([['BAR']]);
});
