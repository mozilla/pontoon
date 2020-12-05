import React from 'react';

import { shallow } from 'enzyme';

import CheckboxTable from 'widgets/tables/checkbox';

test('CheckboxTable render', () => {
    // Test the rendering of the checkboxes table widget

    const table = shallow(<CheckboxTable />);
    expect(table.text()).toBe('<ReactTable />');
    expect(table.instance().columnSelect).toEqual({
        Cell: table.instance().renderCheckbox,
        Header: table.instance().renderSelectAllCheckbox,
        sortable: false,
        width: 45,
    });
    expect(table.instance().defaultPageSize).toBe(5);
});

test('CheckboxTable renderCheckbox', () => {
    // Test the rendering of the checkboxes that control the resources

    const table = shallow(<CheckboxTable />);
    let checkbox = table
        .instance()
        .renderCheckbox({ original: ['FOO'], pageSize: 5 });

    // not checked by default
    expect(checkbox.props.checked).toBe(false);

    // name has been taken from `original` list (the row data)
    expect(checkbox.props.name).toBe('FOO');

    // when the the checkBox changes it fires the handleCheckboxClick evt
    expect(checkbox.props.onChange).toBe(table.instance().handleCheckboxClick);

    // lets setState with some checked items and render one of them
    table.setState({ checked: new Set(['FOO', 'BAR']) });
    checkbox = table
        .instance()
        .renderCheckbox({ original: ['FOO'], pageSize: 5 });

    // the checkbox's props are set appropriately
    expect(checkbox.props.checked).toBe(true);
    expect(checkbox.props.name).toBe('FOO');
    expect(checkbox.props.onChange).toBe(table.instance().handleCheckboxClick);
});

test('CheckboxTable selected', () => {
    // tests the selected attribute of the CheckboxTable.
    // the selected attribute returns the union of visible and checked
    // and responds as to whether all currently visible items are checked

    const table = shallow(<CheckboxTable />);
    let result = table.instance().selected;

    // default is for there to be no checked
    expect(result).toEqual({ all: false, checked: new Set([]) });

    // set some visible items
    table.instance().visible = [4, 5, 6];

    // set checked items
    table.instance().setState({ checked: new Set([1, 2, 3]) });
    result = table.instance().selected;

    // only visible items can be selected
    expect(result).toEqual({ all: false, checked: new Set([]) });

    // set more visible items, including the checked ones
    table.instance().visible = [1, 2, 3, 4, 5, 6];
    result = table.instance().selected;
    expect(result).toEqual({ all: false, checked: new Set([1, 2, 3]) });

    // set *all* visible items to checked
    table.instance().visible = [1, 2, 3];
    result = table.instance().selected;
    expect(result).toEqual({ all: true, checked: new Set([1, 2, 3]) });
});

test('CheckboxTable renderSelectAllCheckbox', () => {
    // tests the selectAll checkbox is properly (shallow) rendered

    const selected = { all: false, checked: new Set() };

    class MockCheckboxTable extends CheckboxTable {
        get selected() {
            return selected;
        }
    }

    const table = shallow(<MockCheckboxTable />);
    let checkbox = table.instance().renderSelectAllCheckbox();

    // by default its not indeterminate or checked, but it does fire
    // this.handleSelectAll when clicked.
    expect(checkbox.props.checked).toBe(false);
    expect(checkbox.props.indeterminate).toBe(false);
    expect(checkbox.props.onClick).toBe(table.instance().handleSelectAll);

    // if some are selected, indeterminate is true but checked is still false
    selected.checked = new Set([1, 2, 3]);
    checkbox = table.instance().renderSelectAllCheckbox();
    expect(checkbox.props.checked).toBe(false);
    expect(checkbox.props.indeterminate).toBe(true);
    expect(checkbox.props.onClick).toBe(table.instance().handleSelectAll);

    // if all are selected then indeterminate is false, and checked is true
    selected.all = true;
    checkbox = table.instance().renderSelectAllCheckbox();
    expect(checkbox.props.checked).toBe(true);
    expect(checkbox.props.indeterminate).toBe(false);
    expect(checkbox.props.onClick).toBe(table.instance().handleSelectAll);
});

test('CheckboxTable handleSelectAll', () => {
    // Tests that when select all is clicked, the checkboxes are checked
    // or cleared appropriately

    const table = shallow(<CheckboxTable />);
    table.instance().setState = jest.fn(() => 23);

    table.instance().handleSelectAll();

    // setState was called with an empty checked set - ie cleared
    // as there are no visible resources
    let stateFunc = table.instance().setState.mock.calls[0][0];
    expect(stateFunc(table.state())).toEqual({ checked: new Set([]) });

    // lets add some visible resources
    table.instance().visible = [1, 2, 3];

    // fire handleSelectAll again...
    table.instance().handleSelectAll();

    // this time setState is called with all of the visible items
    stateFunc = table.instance().setState.mock.calls[1][0];
    expect(stateFunc(table.state())).toEqual({ checked: new Set([1, 2, 3]) });

    // calling handleSelectAll will clear any checked items
    // if they are not visible
    table.instance().state.checked = new Set([4, 5]);
    table.instance().handleSelectAll();
    stateFunc = table.instance().setState.mock.calls[2][0];
    expect(stateFunc(table.state())).toEqual({ checked: new Set() });
});

test('CheckboxTable handleTableSortChange', () => {
    // Tests what happens when the table sort is changed.
    // The expectation is that any items in state.checked are
    // removed if they are no longer visible

    const table = shallow(<CheckboxTable />);

    // only 23 is now in both visible and checked
    table.instance().visible = [23, 113];
    table.setState({ checked: new Set([23, 43]) });
    table.instance().setState = jest.fn(() => 113);

    table.instance().handleTableSortChange();

    // setState is called with a checked set containing just 23
    let stateFunc = table.instance().setState.mock.calls[0][0];
    expect(stateFunc(table.state())).toEqual({ checked: new Set([23]) });
});

test('CheckboxTable handleTableChange', () => {
    // Tests what happens when the table pagination changes
    // expectation is for the checked set to be cleared
    // and the visible list to be truncated

    const table = shallow(<CheckboxTable />);
    table.instance().visible = [23, 43];
    table.setState({ checked: new Set([23, 43]) });
    table.instance().setState = jest.fn(() => 113);

    table.instance().handleTableChange();

    // visible.length is 0
    expect(table.instance().visible.length).toBe(0);

    // setState was called with an empty set
    expect(table.instance().setState.mock.calls).toEqual([
        [{ checked: new Set() }],
    ]);
});

test('CheckboxTable handleTableResize', () => {
    // Tests what happens when the table is resized
    // The expectation is that any items in the checked set
    // that are no longer visible are removed and the visible
    // list is resized accordingly

    const table = shallow(<CheckboxTable />);

    // visible and checked have 2 items in common
    table.instance().visible = [23, 43];
    table.setState({ checked: new Set([23, 43, 73]) });
    table.instance().setState = jest.fn(() => 113);

    table.instance().handleTableResize(5);

    // visible is filled to pageSize
    expect(table.instance().visible).toEqual([
        23,
        43,
        undefined,
        undefined,
        undefined,
    ]);

    // state.checked gets the common items
    let stateFunc = table.instance().setState.mock.calls[0][0];
    expect(stateFunc(table.state())).toEqual({ checked: new Set([23, 43]) });
});

test('CheckboxTable prune', () => {
    // Tests pruning the checked set from the visible list

    const table = shallow(<CheckboxTable />);
    let result = table.instance().prune(table.state());

    // visible is empty so result is empty set
    expect(result).toEqual(new Set([]));

    // lets add some items to checked and visible with
    // some in common
    table.instance().visible = [1, 3, 5];
    table.setState({ checked: new Set([0, 1, 2, 3]) });

    // pruned returns the common set
    expect(table.instance().prune(table.state())).toEqual(new Set([1, 3]));
});

test('CheckboxTable handleSubmit', async () => {
    // Checks what happens when the form is submitted, to add
    // or remove associated resources

    const handleSubmit = jest.fn(async () => 23);
    const table = shallow(<CheckboxTable handleSubmit={handleSubmit} />);
    const evt = { preventDefault: jest.fn() };

    // handleSubmit returns a Promise
    await table.instance().handleSubmit(evt);

    // evt.preventDefault was called
    expect(evt.preventDefault.mock.calls).toEqual([[]]);

    // the call was bubbled to props.handleSubmit with an empty list for data...
    expect(handleSubmit.mock.calls).toEqual([[{ data: [] }]]);

    // ... as state.checked is empty
    expect(table.state().checked).toEqual(new Set());

    // lets add some checked items and fire again
    table.instance().state.checked = new Set([1, 2, 3]);
    await table.instance().handleSubmit(evt);

    // this time props.handleSubmit gets called with an array
    // from the set, and evt.preventDefault was fired again
    expect(handleSubmit.mock.calls[1]).toEqual([{ data: [1, 2, 3] }]);
    expect(evt.preventDefault.mock.calls[1]).toEqual([]);

    // state.checked got cleared
    expect(table.state().checked).toEqual(new Set());
});

test('CheckboxTable handleCheckboxClick', () => {
    // Tests that when a checkbox is clicked it is added/remove
    // from the state.checked set, and that evt.preventDefault is fired

    const table = shallow(<CheckboxTable />);

    // create a fake evt
    const evt = {
        preventDefault: jest.fn(),
        target: { checked: false, name: 23 },
    };

    // fire handleCheckboxClick with it...
    table.instance().handleCheckboxClick(evt);

    // nothing was added as checked=false
    const checked = new Set();
    expect(table.state()).toEqual({ checked });

    // lets make checked=true and handle again...
    evt.target.checked = true;
    table.instance().handleCheckboxClick(evt);
    checked.add(23);

    // this time we get the named item in the checked set
    expect(table.state()).toEqual({ checked });

    // firing again does nothing
    table.instance().handleCheckboxClick(evt);
    expect(table.state()).toEqual({ checked });

    // calling with checked=false removes the item
    evt.target.checked = false;
    table.instance().handleCheckboxClick(evt);
    checked.delete(23);
    expect(table.state()).toEqual({ checked });
});

test('CheckboxTable componentWillReceiveProps', () => {
    // tests the CheckboxTable componentWillReceiveProps method

    const data = [23];
    const table = shallow(<CheckboxTable data={data} />);

    // visible is the (tracked) currently visible resources
    table.instance().visible = [1, 2, 3];

    // lets setState with some "checked" data
    table.setState({ checked: new Set(['a', 'b', 'c']) });
    table.instance().UNSAFE_componentWillReceiveProps({ data });

    // checked has been updated, an visible has remained the same
    expect(table.state().checked).toEqual(new Set(['a', 'b', 'c']));
    expect(table.instance().visible).toEqual([1, 2, 3]);

    // this time lets update the *data* (like when new data comes back
    // from ajax).
    table.instance().UNSAFE_componentWillReceiveProps({ data: [7] });

    // nothing checked or visible round here no more
    expect(table.state().checked).toEqual(new Set([]));
    expect(table.instance().visible).toEqual([]);
});
