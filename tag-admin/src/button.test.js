import { shallow } from 'enzyme';
import React from 'react';

import { TagResourcesButton } from './button.js';

test('TagResourcesButton renders only button initially', () => {
    const button = shallow(
        <TagResourcesButton tag='foo' api='bar' project='baz' />,
    );
    expect(button.html()).toBe(
        '<div><button>Manage resources for this tag</button></div>',
    );
});

test('TagResourcesButton shows TagResourceManager when clicked', () => {
    const button = shallow(
        <TagResourcesButton tag='foo' api='bar' project='baz' />,
    );

    const preventDefault = jest.fn();
    button.find('button').simulate('click', { preventDefault });
    expect(button.html()).toMatch('<div class="tag-resource-widget">');
    expect(preventDefault).toHaveBeenCalled();
});

test('TagResourcesButton renders only Button when clicked twice', () => {
    const button = shallow(
        <TagResourcesButton tag='foo' api='bar' project='baz' />,
    );

    button.find('button').simulate('click', { preventDefault: () => {} });
    expect(button.html()).toMatch('Hide the resource manager for this tag');

    button.find('button').simulate('click', { preventDefault: () => {} });
    expect(button.html()).toMatch('Manage resources for this tag');
});
