import { mount } from 'enzyme';
import React from 'react';
import { act } from 'react-dom/test-utils';

import { TagResourceManager } from './manager.js';

// async fetch response handler needs a tick to process
const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

test('TagResourceManager search', async () => {
    document.querySelector = jest.fn(() => ({ value: '73' }));
    window.fetch = jest.fn(async () => ({
        status: 200,
        json: async () => ({ data: [] }),
    }));

    const manager = mount(<TagResourceManager api='x' />);

    // Enter 'FOO' in the search input
    manager
        .find('input.search-tag-resources')
        .simulate('change', { target: { value: 'FOO' } });
    await act(async () => {
        await flushPromises();
    });

    const { calls } = window.fetch.mock;
    expect(calls).toHaveLength(2);

    expect(Array.from(calls[0][1].body.entries())).toMatchObject([
        ['search', ''],
        ['type', 'assoc'],
        ['csrfmiddlewaretoken', '73'],
    ]);

    expect(Array.from(calls[1][1].body.entries())).toMatchObject([
        ['search', 'FOO'],
        ['type', 'assoc'],
        ['csrfmiddlewaretoken', '73'],
    ]);
});

test('TagResourceManager checkboxing', async () => {
    document.querySelector = jest.fn(() => ({ value: '73' }));
    window.fetch = jest.fn(async () => ({
        status: 200,
        json: async () => ({ data: [['foo'], ['bar']] }),
    }));

    const manager = mount(<TagResourceManager api='y' />);

    await act(async () => {
        await flushPromises();
    });
    manager.update();

    // Check the 'foo' checkbox
    manager
        .find('input[name="foo"]')
        .simulate('change', { target: { name: 'foo', checked: true } });

    // Click on 'Unlink resources'
    manager
        .find('button.tag-resources-associate')
        .simulate('click', { preventDefault: () => {} });

    await act(async () => {
        await flushPromises();
    });

    const { calls } = window.fetch.mock;
    expect(calls).toHaveLength(2);

    expect(Array.from(calls[0][1].body.entries())).toMatchObject([
        ['search', ''],
        ['type', 'assoc'],
        ['csrfmiddlewaretoken', '73'],
    ]);

    expect(Array.from(calls[1][1].body.entries())).toMatchObject([
        ['data', 'foo'],
        ['search', ''],
        ['type', 'assoc'],
        ['csrfmiddlewaretoken', '73'],
    ]);
});
