import { mount, shallow } from 'enzyme';
import React from 'react';
import { act } from 'react-dom/test-utils';

import { CheckboxTable } from './checkbox-table.js';

test('CheckboxTable render', () => {
    const table = shallow(<CheckboxTable />);
    expect(table.text()).toBe('<ReactTable />');
});

test('CheckboxTable render checkboxes', () => {
    const table = mount(<CheckboxTable data={[]} />);
    expect(table.find('input[type="checkbox"]')).toHaveLength(1);

    table.setProps({ data: [['foo'], ['bar']] });
    table.update();
    expect(table.find('input[type="checkbox"]')).toHaveLength(3);

    expect(table.find('input[name="foo"]').getDOMNode().checked).toBe(false);
    expect(table.find('input[name="bar"]').getDOMNode().checked).toBe(false);
});

test('CheckboxTable select checkboxes', () => {
    const table = mount(<CheckboxTable data={[['foo'], ['bar']]} />);
    const inputs = table.find('input[type="checkbox"]');
    expect(inputs).toHaveLength(3);
    let checkbox = inputs.at(0).getDOMNode();

    // Start with no selections
    expect(checkbox.checked).toBe(false);
    expect(checkbox.indeterminate).toBe(false);

    // Select 'foo'
    table
        .find('input[name="foo"]')
        .simulate('change', { target: { name: 'foo', checked: true } });
    checkbox = table.find('input[type="checkbox"]').at(0).getDOMNode();
    expect(checkbox.checked).toBe(false);
    expect(checkbox.indeterminate).toBe(true);

    // Select also 'bar'
    table
        .find('input[name="bar"]')
        .simulate('change', { target: { name: 'bar', checked: true } });
    checkbox = table.find('input[type="checkbox"]').at(0).getDOMNode();
    expect(checkbox.checked).toBe(true);
    expect(checkbox.indeterminate).toBe(false);

    // Unselect all
    inputs.at(0).simulate('change', {});
    expect(table.find('input[name="foo"]').getDOMNode().checked).toBe(false);
    expect(table.find('input[name="bar"]').getDOMNode().checked).toBe(false);

    // Select all
    inputs.at(0).simulate('change', {});
    expect(table.find('input[name="foo"]').getDOMNode().checked).toBe(true);
    expect(table.find('input[name="bar"]').getDOMNode().checked).toBe(true);

    // Unselect 'foo'
    table
        .find('input[name="foo"]')
        .simulate('change', { target: { name: 'foo', checked: false } });
    checkbox = table.find('input[type="checkbox"]').at(0).getDOMNode();
    expect(checkbox.checked).toBe(false);
    expect(checkbox.indeterminate).toBe(true);
});

test('CheckboxTable sort change', () => {
    // Tests what happens when the table sort is changed.
    // The expectation is that any items in state.checked are
    // removed if they are no longer visible

    const table = mount(
        <CheckboxTable
            data={[['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7']]}
        />,
    );

    // Select '2' and '3'
    table
        .find('input[name="2"]')
        .simulate('change', { target: { name: '2', checked: true } });
    table
        .find('input[name="3"]')
        .simulate('change', { target: { name: '3', checked: true } });

    // Click twice to use descending sort, which sets checkboxes 7..3 visible
    const th = table.find('.rt-th.-cursor-pointer');
    th.simulate('click', {});
    th.simulate('click', {});

    expect(table.find('input[name="2"]')).toHaveLength(0);
    expect(table.find('input[name="3"]').getDOMNode().checked).toBe(true);

    // Switch back to ascending sort
    th.simulate('click', {});

    expect(table.find('input[name="2"]').getDOMNode().checked).toBe(false);
    expect(table.find('input[name="3"]').getDOMNode().checked).toBe(true);
});

test('CheckboxTable page change', () => {
    const table = mount(
        <CheckboxTable
            data={[['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7']]}
        />,
    );

    expect(table.find('input[name="2"]')).toHaveLength(1);
    expect(table.find('input[name="6"]')).toHaveLength(0);

    // Click 'Next' button
    const buttons = table.find('button.-btn');
    expect(buttons).toHaveLength(2);
    buttons.at(1).simulate('click', {});

    expect(table.find('input[name="2"]')).toHaveLength(0);
    expect(table.find('input[name="6"]')).toHaveLength(1);
});

test('CheckboxTable resize', () => {
    const table = mount(
        <CheckboxTable
            data={[['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7']]}
        />,
    );

    // Resize to 10 rows
    const select = table.find('.-pageSizeOptions select');
    select.simulate('change', { target: { value: '10' } });

    // Select '2' and '6'
    table
        .find('input[name="2"]')
        .simulate('change', { target: { name: '2', checked: true } });
    table
        .find('input[name="6"]')
        .simulate('change', { target: { name: '6', checked: true } });

    // Resize to 5 rows
    select.simulate('change', { target: { value: '5' } });

    expect(table.find('input[name="2"]').getDOMNode().checked).toBe(true);
    expect(table.find('input[name="6"]')).toHaveLength(0);

    // Resize to 10 rows
    select.simulate('change', { target: { value: '10' } });

    expect(table.find('input[name="2"]').getDOMNode().checked).toBe(true);
    expect(table.find('input[name="6"]').getDOMNode().checked).toBe(false);
});

test('CheckboxTable submit', async () => {
    const spy = jest.fn();
    const table = mount(
        <CheckboxTable
            data={[['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7']]}
            onSubmit={spy}
        />,
    );

    // Select '2' and '3'
    table
        .find('input[name="2"]')
        .simulate('change', { target: { name: '2', checked: true } });
    table
        .find('input[name="3"]')
        .simulate('change', { target: { name: '3', checked: true } });

    // Submit changes
    table
        .find('button.tag-resources-associate')
        .simulate('click', { preventDefault: () => {} });
    await act(() => new Promise((resolve) => setTimeout(resolve, 0)));
    table.update();

    expect(spy.mock.calls).toEqual([[{ data: ['2', '3'] }]]);
    expect(table.find('input[name="2"]').getDOMNode().checked).toBe(false);
    expect(table.find('input[name="3"]').getDOMNode().checked).toBe(false);
});

test('CheckboxTable props change', () => {
    const data = [['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7']];
    const table = mount(<CheckboxTable data={data} />);

    // Select '2' and '3'
    table
        .find('input[name="2"]')
        .simulate('change', { target: { name: '2', checked: true } });
    table
        .find('input[name="3"]')
        .simulate('change', { target: { name: '3', checked: true } });

    expect(table.find('input[name="2"]').getDOMNode().checked).toBe(true);
    expect(table.find('input[name="3"]').getDOMNode().checked).toBe(true);

    // Re-setting props clears checkboxes
    table.setProps({ data: [...data] });
    table.update();

    expect(table.find('input[name="2"]').getDOMNode().checked).toBe(false);
    expect(table.find('input[name="3"]').getDOMNode().checked).toBe(false);
});
