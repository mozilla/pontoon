
import React from 'react';
import ReactDOM from 'react-dom';

import ReactTable from 'react-table';

import {shallow} from 'enzyme';

import {Container} from 'widgets/columns';

import {ajax} from 'utils/ajax';

import {TagResourcesButton, TagResourcesLoader} from 'tags/admin/';

import TagResourceManager from 'tags/admin/manager';
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


test('TagResourceManager render', () => {
    // shallow rendering of TagResourceManager

    const _refreshData = jest.fn();

    class MockTagResourceManager extends TagResourceManager {

        async refreshData () {
            _refreshData();
        }
    }

    const manager = shallow(<MockTagResourceManager />);

    // The TagResourceManager has 3 sub components
    expect(manager.text()).toBe("<TagResourceSearch /><ErrorList /><TagResourceTable />");

    // enzyme.shallow triggers `componentDidUpdate` - so we expect
    // refreshData to have been called (with no args, once)
    expect(_refreshData.mock.calls).toEqual([[]]);
});


test('TagResourceManager handleSearchChange', async () => {
    // Tests what happens when the user makes a change to the search furniture
    // Its expected to call refreshData, after updating state appropriately.

    const _refreshData = jest.fn();

    class MockTagResourceManager extends TagResourceManager {

        async refreshData () {
            _refreshData();
            return 23;
        }
    }

    const manager = shallow(<MockTagResourceManager />);
    const evt = {target: {nodeName: 'INPUT', value: "FOO"}};

    // something changed...
    let result = await manager.instance().handleSearchChange(evt);

    // refreshData was called and returned
    expect(result).toBe(23);

    // it has been called twice now, because it was called when
    // component was (shallow) rendered (with no args).
    expect(_refreshData.mock.calls).toEqual([[], []]);

    // as our mock event was text input, we have updated the
    // search string in `state`
    expect(manager.state()).toEqual(
        {type: 'assoc', search: 'FOO', data: [], errors: {}});
    evt.target.nodeName = 'SELECT';
    evt.target.value = 'BAR';

    // trigger another event - this time to change the action
    // type - ie assoc <> disassoc resources.
    result = await manager.instance().handleSearchChange(evt);
    expect(result).toBe(23);

    // refreshData was called again!
    expect(_refreshData.mock.calls).toEqual([[], [], []]);

    // this time the `type` was changed, but our search string
    // still stands.
    expect(manager.state()).toEqual(
        {type: 'BAR', search: 'FOO', data: [], errors: {}});
});


test('TagResourceManager handleResponse errors', async () => {
    // Tests error handling in the ResourceManager widget

    const _refreshData = jest.fn();

    class MockTagResourceManager extends TagResourceManager {

        async refreshData () {
            _refreshData();
        }
    }

    const manager = shallow(<MockTagResourceManager />);
    manager.instance().setState = jest.fn(async () => 23);
    const response = {status: 500, json: jest.fn(async () => ({}))};

    // trigger handleResponse with bad status
    let result = await manager.instance().handleResponse(response);

    // the Promise of setState was returned
    expect(result).toBe(23);

    // setState was called with our errors, which we didnt specify, but thats ok.
    expect(manager.instance().setState.mock.calls).toEqual([[{"errors": undefined}]]);

    // lets see what happens when we specify errors.
    response.json = jest.fn(async () => ({errors: {foo: 'bad', bar: 'stuff'}}));
    result = await manager.instance().handleResponse(response);

    // we still get back the Promise
    expect(result).toBe(23);

    // but this time setState was called with the errors
    expect(manager.instance().setState.mock.calls[1]).toEqual(
        [{"errors": {"bar": "stuff", "foo": "bad"}}]);
});


test('TagResourceManager handleResponse', async () => {
    // Tests what happens when the manager component receives a response
    // from ajax requests.
    // This can either be the result of a search operation or as a
    // consequence of dis/associating resources to a tag.

    const _refreshData = jest.fn();

    class MockTagResourceManager extends TagResourceManager {

        async refreshData () {
            _refreshData();
        }
    }

    const manager = shallow(<MockTagResourceManager />);
    manager.instance().setState = jest.fn(async () => 23);
    const response = {status: 200, json: jest.fn(async () => ({}))};

    // lets trigger an event with good status
    let result = await manager.instance().handleResponse(response);

    // we get back the Promise of a state to be set
    expect(result).toBe(23);

    // we didnt specify any data, but thats OK, and we dont expect any errors
    expect(manager.instance().setState.mock.calls).toEqual(
        [[{"data": undefined, "errors": {}}]]);

    // lets handle a response with some actual data
    response.json = jest.fn(async () => ({result: {foo: 'good', bar: 'stuff'}}));
    result = await manager.instance().handleResponse(response);

    // we got back the promise again
    expect(result).toBe(23);

    // and setState was called with some lovely data.
    expect(manager.instance().setState.mock.calls[1]).toEqual(
        [{"data": {"bar": "stuff", "foo": "good"}, "errors": {}}]);
});


test('TagResourceManager handleSubmit', async () => {
    // Tests what happens when user clicks handleSubmit

    const response = {json: async () => '113'};
    ajax.post = jest.fn(async () => response);
    const manager = await shallow(<TagResourceManager api={43} />);
    const instance = manager.instance();

    instance.handleResponse = jest.fn(async () => 23);

    // ajax gets fired from componentDidMount, so lets clear it
    ajax.post.mockClear();

    let result = await instance.handleSubmit(7);

    // we expect the async response from handleResponse to be returned
    expect(result).toBe(23);

    // handleResponse gets called with the Promise of some json from ajax
    expect(manager.instance().handleResponse.mock.calls).toEqual([[response]]);

    // and ajax got called with all of the expected post data.
    expect(ajax.post.mock.calls).toEqual(
        [[43, {"paths": 7, "search": "*", "type": "assoc"}]]);
});




test('TagResourceManager refreshData', async () => {
    // refreshData calls ajax and gives the child components a shakedown
    // with the results. Its called in componentDidMount as well as in
    // response to user actions.

    const manager = await shallow(<TagResourceManager api={43} />);

    manager.instance().handleResponse = jest.fn(async () => 23);
    ajax.post = jest.fn(async () => 37);
    let result = await manager.instance().refreshData();

    // we get back the Promise of a handled Response.
    expect(result).toBe(23);

    // handleResponse was called with the awaited content from ajax.post
    expect(manager.instance().handleResponse.mock.calls).toEqual([[37]]);

    // and ajax.post was called with the expected vars
    expect(ajax.post.mock.calls).toEqual(
        [[43, {"search": "*", "type": "assoc"}]]);
});


test('TagResourceSearch render', () => {
    // tests that the search widget (shallow) renders as expected

    const search = shallow(<TagResourceSearch />);

    // its a container
    expect(search.text()).toBe("<Container />");
    let container = search.find(Container);

    // it has 2 columns
    expect(container.props().columns).toBe(2);

    // they are in proportion 2:3
    expect(container.props().ratios).toEqual([3, 2]);

    // they each have a form widget with some CSS selectors
    expect(search.find('input.search-tag-resources').length).toBe(1);
    expect(search.find('select.search-tag-resource-type').length).toBe(1);
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

    // we should have a ReactTable here
    let reactTable = table.find(ReactTable);

    // and some prompt text depending on action state
    expect(table.text()).toBe("<ReactTable />Link resources");

    // reactTable was created with the correct column descriptors
    expect(reactTable.props().columns).toEqual(table.instance().columns);

    // lets render another table with different action
    table = shallow(<TagResourceTable type="assoc" />);

    // prompt text has changed
    expect(table.text()).toBe("<ReactTable />Unlink resources");

    // but we still get our table
    reactTable = table.find(ReactTable);

    // and the expected columns
    expect(reactTable.props().columns).toEqual(table.instance().columns);
});


test('TagResourceTable columns', () => {
    // tests the column descriptors for the resource table

    let table = shallow(<TagResourceTable />);

    // header[0] is the select all checkbox
    expect(table.instance().columns[0].Header).toBe(
        table.instance().renderSelectAllCheckbox);

    // Cell[0] is the resource checkbox
    expect(table.instance().columns[0].Cell).toBe(
        table.instance().renderResourceCheckbox);

    // Cell[1] is the resource itself.
    expect(table.instance().columns[1].Cell).toBe(
        table.instance().renderResource);
});


test('TagResourceTable componentWillUpdate', async () => {
    // tests the TagResourceTable componentWillUpdate method

    const data = [23];
    const table = shallow(<TagResourceTable data={data} />);

    // visible is the (tracked) currently visible resources
    table.instance().visible = [1, 2, 3];

    // lets setState with some "checked" data
    await table.setState({checked: new Set(['a', 'b', 'c'])});
    table.instance().componentWillUpdate({data});

    // checked has been updated, an visible has remained the same
    expect(table.state().checked).toEqual(new Set(['a', 'b', 'c']));
    expect(table.instance().visible).toEqual([1, 2, 3]);

    // this time lets update the *data* (like when new data comes back
    // from ajax).
    table.instance().componentWillUpdate({data: [7]});

    // nothing checked or visible round here no more
    expect(table.state().checked).toEqual(new Set([]));
    expect(table.instance().visible).toEqual([]);
});


test('TagResourceTable renderResource', () => {
    // When an item is rendered, apart from creating the necessary
    // component, we also expect the pageSize to be updated
    // appropriately, and for the resource to take its place in the
    // visible index.

    const table = shallow(<TagResourceTable />);
    let resource = table.instance().renderResource(
        {original: ['FOO'], viewIndex: 7, pageSize: 23});

    // lets create an array like the one we expect to find
    const expected = [];
    expected.length = 23;
    expected[7] = 'FOO';

    // this.visible is the same as our expected array
    expect(table.instance().visible).toEqual(expected);

    // and our resource has happily rendered
    expect(resource.props.children).toEqual('FOO');
});


test('TagResourceTable renderResourceCheckbox', () => {
    // Test the rendering of the checkboxes that control the resources

    const table = shallow(<TagResourceTable />);
    let checkbox = table.instance().renderResourceCheckbox(
        {original: ['FOO']});

    // not checked by default
    expect(checkbox.props.checked).toBe(false);

    // name has been taken from `original` list (the row data)
    expect(checkbox.props.name).toBe('FOO');

    // when the the checkBox changes it fires the handleCheckboxClick evt
    expect(checkbox.props.onChange).toBe(table.instance().handleCheckboxClick);

    // lets setState with some checked items and render one of them
    table.setState({checked: new Set(['FOO', 'BAR'])});
    checkbox = table.instance().renderResourceCheckbox(
        {original: ['FOO']});

    // the checkbox's props are set appropriately
    expect(checkbox.props.checked).toBe(true);
    expect(checkbox.props.name).toBe('FOO');
    expect(checkbox.props.onChange).toBe(table.instance().handleCheckboxClick);
});


test('TagResourceTable selected', async () => {
    // tests the selected attribute of the TagResourceTable.
    // the selected attribute returns the union of visible and checked
    // and responds as to whether all currently visible items are checked

    const table = shallow(<TagResourceTable />);
    let result = table.instance().selected;

    // default is for there to be no checked
    expect(result).toEqual({all: false, checked: new Set([])});

    // set some visible items
    table.instance().visible = [4, 5, 6];

    // set checked items
    await table.instance().setState({checked: new Set([1, 2, 3])});
    result = table.instance().selected;

    // only visible items can be selected
    expect(result).toEqual({all: false, checked: new Set([])});

    // set more visible items, including the checked ones
    table.instance().visible = [1, 2, 3, 4, 5, 6];
    result = table.instance().selected;
    expect(result).toEqual({all: false, checked: new Set([1, 2, 3])});

    // set *all* visible items to checked
    table.instance().visible = [1, 2, 3];
    result = table.instance().selected;
    expect(result).toEqual({all: true, checked: new Set([1, 2, 3])});
});


test('TagResourceTable renderSelectAllCheckbox', () => {
    // tests the selectAll checkbox is properly (shallow) rendered

    const selected = {all: false, checked: new Set()};

    class MockTagResourceTable extends TagResourceTable {

        get selected () {
            return selected;
        }
    }

    const table = shallow(<MockTagResourceTable />);
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


test('TagResourceTable handleSelectAll', async () => {
    // Tests that when select all is clicked, the checkboxes are checked
    // or cleared appropriately

    const table = shallow(<TagResourceTable />);
    table.instance().setState = jest.fn(() => 23);
    let result = table.instance().handleSelectAll();

    // returns the Promise from setState
    expect(result).toBe(23);

    // setState was called with an empty checked set - ie cleared
    // as there are no visible resources
    expect(table.instance().setState.mock.calls).toEqual(
        [[{"checked": new Set([])}]]);

    // lets add some visible resources
    table.instance().visible = [1, 2, 3];

    // fire handleSelectAll again...
    expect(table.instance().handleSelectAll()).toBe(23);

    // this time setState is called with all of the visible items
    expect(table.instance().setState.mock.calls[1]).toEqual(
        [{"checked": new Set([1, 2, 3])}]);

    // calling handleSelectAll will clear any checked items
    // if they are not visible
    table.instance().state.checked = new Set([4, 5]);
    expect(table.instance().handleSelectAll()).toBe(23);
    expect(table.instance().setState.mock.calls[2]).toEqual(
        [{"checked": new Set()}]);

});


test('TagResourceTable handleTableSortChange', async () => {
    // Tests what happens when the table sort is changed.
    // The expectation is that any items in state.checked are
    // removed if they are no longer visible

    const table = shallow(<TagResourceTable />);

    // only 23 is now in both visible and checked
    table.instance().visible = [23, 113];
    table.setState({checked: new Set([23, 43])});
    table.instance().setState = jest.fn(() => 113);

    // handleTableSortChange returns a promise of state to be set
    let result = table.instance().handleTableSortChange();
    expect(result).toBe(113);

    // setState is called with a checked set containing just 23
    expect(table.instance().setState.mock.calls).toEqual(
        [[{"checked": new Set([23])}]]);
});


test('TagResourceTable handleTableChange', async () => {
    // Tests what happens when the table pagination changes
    // expectation is for the checked set to be cleared
    // and the visible list to be truncated

    const table = shallow(<TagResourceTable />);
    table.instance().visible = [23, 43];
    table.setState({checked: new Set([23, 43])});
    table.instance().setState = jest.fn(() => 113);

    // handleTableChange returns the promise from setState
    let result = table.instance().handleTableChange();
    expect(result).toBe(113);

    // visible.length is 0
    expect(table.instance().visible.length).toBe(0);

    // setState was called with an empty set
    expect(table.instance().setState.mock.calls).toEqual(
        [[{"checked": new Set()}]]);
});


test('TagResourceTable handleTableResize', () => {
    // Tests what happens when the table is resized
    // The expectation is that any items in the checked set
    // that are no longer visible are removed and the visible
    // list is resized accordingly

    const table = shallow(<TagResourceTable />);

    // visible and checked have 2 items in common
    table.instance().visible = [23, 43];
    table.setState({checked: new Set([23, 43, 73])});
    table.instance().setState = jest.fn(() => 113);
    let result = table.instance().handleTableResize(5);
    expect(result).toBe(113);

    // visible is filled to pageSize
    expect(table.instance().visible).toEqual(
        [23, 43, undefined, undefined, undefined]);

    // state.checked gets the common items
    expect(table.instance().setState.mock.calls).toEqual(
        [[{"checked": new Set([23, 43])}]]);
});


test('TagResourceTable pruned', async () => {
    // Tests pruning the checked set from the visible list

    const table = shallow(<TagResourceTable />);
    let result = table.instance().pruned;

    // visible is empty so result is empty set
    expect(result).toEqual(new Set([]));

    // lets add some items to checked and visible with
    // some in common
    table.instance().visible = [1, 3, 5];
    table.setState({checked: new Set([0, 1, 2, 3])});

    // pruned returns the common set
    expect(table.instance().pruned).toEqual(new Set([1, 3]));
});




test('TagResourceTable handleSubmit', async () => {
    // Checks what happens when the form is submitted, to add
    // or remove associated resources

    const handleSubmit = jest.fn(async () => 23);
    const table = shallow(<TagResourceTable handleSubmit={handleSubmit} />);
    const evt = {preventDefault: jest.fn()};

    // handleSubmit returns a Promise
    await table.instance().handleSubmit(evt);

    // evt.preventDefault was called
    expect(evt.preventDefault.mock.calls).toEqual([[]]);

    // the call was bubbled to props.handleSubmit with an empty list...
    expect(handleSubmit.mock.calls).toEqual([[[]]]);

    // ... as state.checked is empty
    expect(table.state().checked).toEqual(new Set());

    // lets add some checked items and fire again
    table.instance().state.checked = new Set([1, 2, 3]);
    await table.instance().handleSubmit(evt);

    // this time props.handleSubmit gets called with an array
    // from the set, and evt.preventDefault was fired again
    expect(handleSubmit.mock.calls[1]).toEqual([[1, 2, 3]]);
    expect(evt.preventDefault.mock.calls[1]).toEqual([]);

    // state.checked got cleared
    expect(table.state().checked).toEqual(new Set());
});



test('TagResourceTable handleCheckboxClick', async () => {
    // Tests that when a checkbox is clicked it is added/remove
    // from the state.checked set, and that evt.preventDefault is fired

    const table = shallow(<TagResourceTable />);

    // create a fake evt
    const evt = {
        preventDefault: jest.fn(),
        target: {checked: false, name: 23}};

    // fire handleCheckboxClick with it...
    table.instance().handleCheckboxClick(evt);

    // nothing was added as checked=false
    const checked = new Set();
    expect(table.state()).toEqual({checked});

    // lets make checked=true and handle again...
    evt.target.checked = true;
    table.instance().handleCheckboxClick(evt);
    checked.add(23);

    // this time we get the named item in the checked set
    expect(table.state()).toEqual({checked});

    // firing again does nothing
    table.instance().handleCheckboxClick(evt);
    expect(table.state()).toEqual({checked});

    // calling with checked=false removes the item
    evt.target.checked = false;
    table.instance().handleCheckboxClick(evt);
    checked.delete(23);
    expect(table.state()).toEqual({checked});
});


test('TagResourcesLoader constructor', () => {
    document.querySelectorAll = jest.fn(() => new Set([1, 2, 3]));
    const loader = new TagResourcesLoader();

    // the loader has a tagResourceNodes property
    const nodes = loader.tagResourceNodes;
    expect(nodes).toEqual([1, 2, 3]);

    // which returns the matching nodes from the DOM
    expect(document.querySelectorAll.mock.calls).toEqual(
        [["div.js-tag-resources"]]);
});


test('TagResourcesLoader addButton', () => {
    // When addButton is called it should take the data nodes
    // from the passed node, call ReactDOM.render with
    // the created button

    const loader = new TagResourcesLoader();
    ReactDOM.render = jest.fn();
    const button = {dataset: {api: 'API0', project: 'PROJECT0', tag: 'TAG0'}};

    // add the button
    loader.addButton(button);

    // get the created button back from the mock call
    const tagButton = ReactDOM.render.mock.calls[0][0];

    // and check its props match those from the dataset
    expect(tagButton.props).toEqual(button.dataset);

    // second arg to ReactDOM.render is node from DOM
    expect(ReactDOM.render.mock.calls[0][1]).toEqual(button);
});


test('TagResourcesLoader addButtons', () => {
    // Tests that addButtons calls addButton for each
    // node found
    document.querySelectorAll = jest.fn(() => ['a', 'b', 'c']);
    const loader = new TagResourcesLoader();
    loader.addButton = jest.fn();

    // add some buttons...
    loader.addButtons();

    // addButton was called with the mocked args
    expect(loader.addButton.mock.calls.map(x => x[0])).toEqual(["a", "b", "c"]);
});


test('TagResourcesLoader loaded', () => {
    // When the DOMContentLoaded is fired the TagResourceLoader.addButtons is
    // fired
    TagResourcesLoader.prototype.addButtons = jest.fn();

    // create a fake event and fire it
    const DOMContentLoaded_event = document.createEvent("Event");
    DOMContentLoaded_event.initEvent("DOMContentLoaded", true, true);
    window.document.dispatchEvent(DOMContentLoaded_event);

    // addButtons was called once and with no args
    expect(TagResourcesLoader.prototype.addButtons.mock.calls).toEqual([[]]);
});
