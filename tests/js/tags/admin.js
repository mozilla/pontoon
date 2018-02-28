
import React from 'react';

import {shallow} from 'enzyme';

import {Columns} from 'widgets/columns';

import {Loader} from 'loaders';
import {DataManager} from 'utils/data';
import {CheckboxTable} from 'widgets/tables';

import TagResourcesLoader from 'tags/admin/';
import TagResourcesButton from 'tags/admin/button';
import {TagResourceDataManager, TagResourceManagerWidget} from 'tags/admin/manager';
import TagResourceSearch from 'tags/admin/search';
import TagResourceTable from 'tags/admin/table';


test('TagResourcesButton render', () => {
    // shallow render of TagResourcesButton to ensure that
    // renderButton and renderResourceManager are called in
    // render method

    class MockTagResourcesButton extends TagResourcesButton {

        renderButton () {
            return 7;
        }

        renderResourceManager () {
            return 23;
        }
    }
    const button = shallow(<MockTagResourcesButton />);
    // just the 2 components
    expect(button.text()).toBe("723");
});


test('TagResourcesButton handleClick', () => {
    // test that TagResourceButton component state is updated
    // appropriately when button is clicked

    const button = shallow(<TagResourcesButton />);
    const evt = {preventDefault: jest.fn()};

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
    expect(result.props.children).toBe("Manage resources for this tag");

    // and the button is set up with the handler
    expect(result.props.onClick).toBe(button.instance().handleClick);

    button.setState({open: true});
    result = button.instance().renderButton();

    // prompt is now to hide the resource manager
    expect(result.props.children).toBe("Hide the resource manager for this tag");

    // and the handler is still set on the component
    expect(result.props.onClick).toBe(button.instance().handleClick);
});


test('TagResourcesButton renderResourceManager', () => {
    // Shallow rendering of the resource manager widget

    const button = shallow(
        <TagResourcesButton
           tag='foo'
           api='bar'
           project='baz' />);
    let result = button.instance().renderResourceManager();

    // nothing there as the resource manager is hidden by default
    expect(result).toBe('');
    button.setState({open: true});

    // now its open - result is an instance of TagResourceManager
    result = button.instance().renderResourceManager();

    // and the TagResourceManager has been inited with the magic props
    expect(result.props.tag).toBe('foo');
    expect(result.props.api).toBe('bar');
    expect(result.props.project).toBe('baz');
});


test('TagResourceDataManager constructor', () => {
    const manager = new TagResourceDataManager();
    expect(manager instanceof DataManager).toBe(true);
    expect(manager.requestMethod).toBe('post');
});


test('TagResourceManagerWidget handleSearchChange', async () => {
    // Tests what happens when the user makes a change to the search furniture
    // Its expected to call refreshData, after updating state appropriately.

    const refreshData = jest.fn(async () => 23);
    const manager = shallow(<TagResourceManagerWidget refreshData={refreshData} />);
    const evt = {target: {nodeName: 'INPUT', value: "FOO"}};

    // something changed...
    let result = await manager.instance().handleSearchChange(evt);

    // refreshData was called and returned
    expect(result).toBe(23);

    // it has been called twice now, because it was called when
    // component was (shallow) rendered
    expect(refreshData.mock.calls).toEqual(
        [[{"search": "*", "type": "assoc"}],
         [{"search": "FOO", "type": "assoc"}]]);

    // as our mock event was text input, we have updated the
    // search string in `state`
    expect(manager.state()).toEqual({type: 'assoc', search: 'FOO'});

    // trigger another event - this time to change the action
    // type - ie assoc <> disassoc resources.
    evt.target.nodeName = 'SELECT';
    evt.target.value = 'BAR';
    result = await manager.instance().handleSearchChange(evt);
    expect(result).toBe(23);

    // refreshData was called again!
    expect(refreshData.mock.calls).toEqual(
        [[{"search": "*", "type": "assoc"}],
         [{"search": "FOO", "type": "assoc"}],
         [{"search": "FOO", "type": "BAR"}]]);

    // this time the `type` was changed, but our search string
    // still stands.
    expect(manager.state()).toEqual({type: 'BAR', search: 'FOO'});
});


test('TagResourceSearch render', () => {
    // tests that the search widget (shallow) renders as expected

    const search = shallow(<TagResourceSearch />);

    // its a container
    expect(search.text()).toBe("<Columns />");
    let container = search.find(Columns);

    // it has 2 columns
    expect(container.props().columns.length).toBe(2);
});


test('TagResourceSearch renderSearchInput', () => {
    // tests the search textinput widget (shallow) renders as expected

    const onChange = jest.fn();
    const search = shallow(<TagResourceSearch handleSearchChange={onChange} />);
    let input = search.instance().renderSearchInput();

    // its an input
    expect(input.type).toBe('input');

    // which has a CSS selector
    expect(input.props.className).toBe('search-tag-resources');

    // and a placeholder prompt for some searchy
    expect(input.props.placeholder).toBe('Search for resources');

    // it fires props.handleSearchChange when changed
    expect(input.props.onChange).toBe(onChange);
});


test('TagResourceSearch renderSearchSelect', () => {
    // Renders the search select widget for changing action
    // - ie dis/associate resources to tag

    const onChange = jest.fn();
    const search = shallow(<TagResourceSearch handleSearchChange={onChange} />);
    let select = search.instance().renderSearchSelect();

    // its a select widget
    expect(select.type).toBe('select');

    // with some CSS selectors
    expect(select.props.className).toBe('search-tag-resource-type');

    // it fires props.handleSearchChange when changed
    expect(select.props.onChange).toBe(onChange);

    // it has 2 options with the expected action values
    expect(select.props.children.length).toBe(2);
    expect(select.props.children[0].props.value).toBe('assoc');
    expect(select.props.children[1].props.value).toBe('nonassoc');
});


test('TagResourceTable render', () => {
    // Tests (shallow) rendering of TagResourceTable

    let table = shallow(<TagResourceTable />);

    // we should have a single CheckboxTable here
    expect(table.text()).toBe("<CheckboxTable />");
    let checkboxTable = table.find(CheckboxTable);
    expect(checkboxTable.length).toBe(1);
    expect(checkboxTable.props().submitMessage).toBe('Link resources');

    // reactTable was created with the correct column descriptors
    expect(checkboxTable.props().columns).toEqual(table.instance().columns);

    // lets render another table with different action
    table = shallow(<TagResourceTable type="assoc" />);

    // prompt text has changed
    // but we still get our table
    expect(table.text()).toBe("<CheckboxTable />");
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
        table.instance().renderResource);
});


test('TagResourceTable renderResource', () => {
    // When an item is rendered, apart from creating the necessary
    // component, we also expect the pageSize to be updated
    // appropriately, and for the resource to take its place in the
    // visible index.

    const table = shallow(<TagResourceTable />);
    let resource = table.instance().renderResource({original: ['FOO']});

    // and our resource has happily rendered
    expect(resource.props.children).toEqual('FOO');
});


test('TagResourcesLoader constructor', () => {
    // checks for expected properties on loader

    const loader = new TagResourcesLoader();
    expect(loader instanceof Loader).toBe(true);
    expect(loader.selector).toBe('.js-tag-resources');
    expect(loader.component).toBe(TagResourcesButton);
});


test('TagResourcesLoader getProps', () => {
    // checks properties are passed through correctly by loader

    const loader = new TagResourcesLoader();
    expect(loader.getProps(
        {dataset: {api: 7, tag: 23, project: 113}})).toEqual(
            {api: 7, tag: 23, project: 113});
});


test('TagResourcesLoader loaded', () => {
    // When the DOMContentLoaded is fired the TagResourceLoader.load is
    // fired
    TagResourcesLoader.prototype.load = jest.fn();

    // create a fake event and fire it
    const DOMContentLoaded_event = document.createEvent("Event");
    DOMContentLoaded_event.initEvent("DOMContentLoaded", true, true);
    window.document.dispatchEvent(DOMContentLoaded_event);

    // load was called once and with no args
    expect(TagResourcesLoader.prototype.load.mock.calls).toEqual([[]]);
});
