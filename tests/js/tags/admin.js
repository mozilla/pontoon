import React from 'react';

import { shallow } from 'enzyme';

import { Columns } from 'widgets/columns';

import CheckboxTable from 'widgets/tables/checkbox';

import TagResourcesButton from 'tags/admin/button';
import { TagResourceManagerWidget } from 'tags/admin/manager';
import TagResourceSearch from 'tags/admin/search';
import TagResourceTable from 'tags/admin/table';

test('TagResourcesButton render', () => {
    // shallow render of TagResourcesButton to ensure that
    // renderButton and renderResourceManager are called in
    // render method

    class MockTagResourcesButton extends TagResourcesButton {
        renderButton() {
            return 7;
        }

        renderResourceManager() {
            return 23;
        }
    }
    const button = shallow(<MockTagResourcesButton />);
    // just the 2 components
    expect(button.text()).toBe('723');
});

test('TagResourcesButton handleClick', () => {
    // test that TagResourceButton component state is updated
    // appropriately when button is clicked

    const button = shallow(<TagResourcesButton />);
    const evt = { preventDefault: jest.fn() };

    // button is closed by default
    expect(button.state().open).toBe(false);

    // click the button
    button.instance().handleClick(evt);

    // component state is not `open`
    expect(button.state().open).toBe(true);

    // evt.preventDefault was called
    expect(evt.preventDefault.mock.calls).toEqual([[]]);

    // click the button again
    button.instance().handleClick(evt);

    // button was closed again
    expect(button.state().open).toBe(false);

    // evt.preventDefault has been called again
    expect(evt.preventDefault.mock.calls).toEqual([[], []]);
});

test('TagResourcesButton renderButton', () => {
    // test that renderButton creates component with expected props and
    // displays appropriate message according to whether its open/cosed

    const button = shallow(<TagResourcesButton />);
    let result = button.instance().renderButton();

    // by default prompt is to manage resources
    expect(result.props.children).toBe('Manage resources for this tag');

    // and the button is set up with the handler
    expect(result.props.onClick).toBe(button.instance().handleClick);

    button.setState({ open: true });
    result = button.instance().renderButton();

    // prompt is now to hide the resource manager
    expect(result.props.children).toBe(
        'Hide the resource manager for this tag',
    );

    // and the handler is still set on the component
    expect(result.props.onClick).toBe(button.instance().handleClick);
});

test('TagResourcesButton renderResourceManager', () => {
    // Shallow rendering of the resource manager widget

    const button = shallow(
        <TagResourcesButton tag='foo' api='bar' project='baz' />,
    );
    let result = button.instance().renderResourceManager();

    // nothing there as the resource manager is hidden by default
    expect(result).toBe('');
    button.setState({ open: true });

    // now its open - result is an instance of TagResourceManager
    result = button.instance().renderResourceManager();

    // and the TagResourceManager has been inited with the magic props
    expect(result.props.tag).toBe('foo');
    expect(result.props.api).toBe('bar');
    expect(result.props.project).toBe('baz');
});

test('TagResourceManagerWidget componentDidUpdate', async () => {
    const refreshData = jest.fn();
    const manager = shallow(
        <TagResourceManagerWidget refreshData={refreshData} />,
    );
    refreshData.mockClear();

    // state is the same, refreshData not called
    manager.instance().componentDidUpdate(undefined, manager.state());
    expect(refreshData.mock.calls).toEqual([]);

    // state "changed", refreshData called with current state
    const prevState = Object.assign({}, manager.state(), { foo: 7, bar: 23 });
    manager.instance().componentDidUpdate(undefined, prevState);
    expect(refreshData.mock.calls).toEqual([[manager.state()]]);
});

test('TagResourceManagerWidget handleSubmit', async () => {
    // Tests that handleSubmit calls this.props.handleSubmit with state and the
    // calling object

    const handleSubmit = jest.fn(async () => 23);
    const refreshData = jest.fn();
    const manager = shallow(
        <TagResourceManagerWidget
            refreshData={refreshData}
            handleSubmit={handleSubmit}
        />,
    );
    manager.setState({ foo: 7, bar: 23 });
    expect(await manager.instance().handleSubmit({ bar: 43, baz: 73 })).toBe(
        23,
    );
    expect(handleSubmit.mock.calls).toEqual([
        [{ bar: 43, baz: 73, foo: 7, search: '', type: 'assoc' }],
    ]);
});

test('TagResourceManagerWidget handleSearchChange', async () => {
    // Tests what happens when the user makes a change to the search furniture
    // Its expected to call refreshData, after updating state appropriately.

    const refreshData = jest.fn(async () => 23);
    const manager = shallow(
        <TagResourceManagerWidget refreshData={refreshData} />,
    );

    // something changed...
    manager.instance().handleSearchChange({ foo: 7, search: 23 });

    // state was updated
    expect(manager.state()).toEqual({ foo: 7, search: 23, type: 'assoc' });
});

test('TagResourceSearch render', () => {
    // tests that the search widget (shallow) renders as expected

    const search = shallow(<TagResourceSearch />);

    // its a container
    expect(search.text()).toBe('<Columns />');
    let container = search.find(Columns);

    // it has 2 columns
    expect(container.props().columns.length).toBe(2);
});

test('TagResourceSearch renderSearchInput', () => {
    // tests the search textinput widget (shallow) renders as expected

    const search = shallow(<TagResourceSearch />);
    let input = search.instance().renderSearchInput();

    // its an input
    expect(input.type).toBe('input');

    // which has a CSS selector
    expect(input.props.className).toBe('search-tag-resources');

    // and a placeholder prompt for some searchy
    expect(input.props.placeholder).toBe('Search for resources');

    // it fires props.handleSearchChange when changed
    expect(input.props.onChange).toBe(search.instance().handleChange);
});

test('TagResourceSearch renderSearchSelect', () => {
    // Renders the search select widget for changing action
    // - ie dis/associate resources to tag

    const search = shallow(<TagResourceSearch />);
    let select = search.instance().renderSearchSelect();

    // its a select widget
    expect(select.type).toBe('select');

    // with some CSS selectors
    expect(select.props.className).toBe('search-tag-resource-type');

    // it fires props.handleSearchChange when changed
    expect(select.props.onChange).toBe(search.instance().handleChange);

    // it has 2 options with the expected action values
    expect(select.props.children.length).toBe(2);
    expect(select.props.children[0].props.value).toBe('assoc');
    expect(select.props.children[1].props.value).toBe('nonassoc');
});

test('TagResourceSearch handleChange', async () => {
    const handleChange = jest.fn(async () => 23);
    const search = shallow(
        <TagResourceSearch handleSearchChange={handleChange} />,
    );

    // onChange was called with search and returned
    const evt = { target: { name: 'SEARCH', value: 'FOO' } };
    let result = await search.instance().handleChange(evt);
    expect(result).toBe(23);
    expect(handleChange.mock.calls).toEqual([[{ SEARCH: 'FOO' }]]);

    handleChange.mockClear();

    // onChange was called with type and returned
    evt.target = { name: 'TYPE', value: 'BAR' };
    result = await search.instance().handleChange(evt);
    expect(result).toBe(23);
    expect(handleChange.mock.calls).toEqual([[{ TYPE: 'BAR' }]]);
});

test('TagResourceTable render', () => {
    // Tests (shallow) rendering of TagResourceTable

    let table = shallow(<TagResourceTable />);

    // we should have a single CheckboxTable here
    expect(table.text()).toBe('<CheckboxTable />');
    let checkboxTable = table.find(CheckboxTable);
    expect(checkboxTable.length).toBe(1);
    expect(checkboxTable.props().submitMessage).toBe('Link resources');

    // reactTable was created with the correct column descriptors
    expect(checkboxTable.props().columns).toEqual(table.instance().columns);

    // lets render another table with different action
    table = shallow(<TagResourceTable type='assoc' />);

    // prompt text has changed
    // but we still get our table
    expect(table.text()).toBe('<CheckboxTable />');
    checkboxTable = table.find(CheckboxTable);
    expect(checkboxTable.length).toBe(1);
    expect(checkboxTable.props().submitMessage).toBe('Unlink resources');

    // and the expected columns
    expect(checkboxTable.props().columns).toEqual(table.instance().columns);
});

test('TagResourceTable columns', () => {
    // tests the column descriptors for the resource table

    let table = shallow(<TagResourceTable />);
    let checkboxTable = table.find(CheckboxTable);

    // Cell[1] is the resource itself.
    expect(checkboxTable.props().columns[0].Cell).toBe(
        table.instance().renderResource,
    );
});

test('TagResourceTable renderResource', () => {
    // When an item is rendered, apart from creating the necessary
    // component, we also expect the pageSize to be updated
    // appropriately, and for the resource to take its place in the
    // visible index.

    const table = shallow(<TagResourceTable />);
    let resource = table.instance().renderResource({ original: ['FOO'] });

    // and our resource has happily rendered
    expect(resource.props.children).toEqual('FOO');
});
