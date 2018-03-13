
import React from 'react';

import {shallow} from 'enzyme';

import {ajax} from 'utils/ajax';

import {DataManager, dataManager} from 'utils/data';


test('DataManager constructor', () => {
    const component = {state: {data: 'FOO', errors: 'BAR'}, props: {api: 'BAZ'}};
    const manager = new DataManager(component);
    expect(manager.component).toBe(component);
    expect(manager.data).toBe('FOO');
    expect(manager.errors).toBe('BAR');
    expect(manager.api).toBe('BAZ');
    expect(manager.requestMethod).toBe('get');
    expect(manager.submitMethod).toBe('get');
});


test('DataManager requestMethod', () => {
    // requestMethod can be overriden in props
    const component = {props: {requestMethod: 23}};
    const manager = new DataManager(component);
    expect(manager.requestMethod).toBe(23);
    expect(manager.submitMethod).toBe(23);
});


test('DataManager submitMethod', () => {
    // submitMethod can be overriden in props
    const component = {props: {submitMethod: 7}};
    const manager = new DataManager(component);
    expect(manager.requestMethod).toBe('get');
    expect(manager.submitMethod).toBe(7);
});


test('DataManager refreshData', async () => {
    // refreshData calls ajax and gives the child components a shakedown
    // with the results. Its called in componentDidMount as well as in
    // response to user actions.

    const manager = new DataManager({props: {api: 43}});
    manager.handleResponse = jest.fn(async () => 23);
    ajax.get = jest.fn(async () => 37);
    let result = await manager.refreshData({foo: 'BAR'});

    // we get back the Promise of a handled Response.
    expect(result).toBe(23);

    // handleResponse was called with the awaited content from ajax.get
    expect(manager.handleResponse.mock.calls).toEqual([[37]]);

    // and ajax.get was called with the expected vars
    expect(ajax.get.mock.calls).toEqual([[43, {"foo": "BAR"}]]);
});


test('DataManager handleSubmit', async () => {
    // Tests what happens when user clicks handleSubmit

    const manager = new DataManager({props: {api: 43}});
    const response = {json: async () => '113'};
    ajax.get = jest.fn(async () => response);

    manager.handleResponse = jest.fn(async () => 23);

    // ajax gets fired from componentDidMount, so lets clear it
    ajax.get.mockClear();

    let result = await manager.handleSubmit(7);

    // we expect the async response from handleResponse to be returned
    expect(result).toBe(23);

    // handleResponse gets called with the Promise of some json from ajax
    expect(manager.handleResponse.mock.calls).toEqual([[response]]);

    // and ajax got called with all of the expected post data.
    expect(ajax.get.mock.calls).toEqual([[43, 7]]);
});


test('DataManager handleResponse errors', async () => {
    // Tests error handling in the ResourceManager widget

    const component = {setState: jest.fn(async () => 23)};
    const manager = new DataManager(component);

    // trigger handleResponse with bad status
    const response = {status: 500, json: jest.fn(async () => ({}))};
    await manager.handleResponse(response);

    // setState was called with our errors, which we didnt specify, but thats ok.
    expect(manager.component.setState.mock.calls).toEqual([[{"errors": undefined}]]);

    // lets see what happens when we specify errors.
    response.json = jest.fn(async () => ({errors: {foo: 'bad', bar: 'stuff'}}));
    await manager.handleResponse(response);

    // but this time setState was called with the errors
    expect(manager.component.setState.mock.calls[1]).toEqual(
        [{"errors": {"bar": "stuff", "foo": "bad"}}]);
});


test('DataManager handleResponse', async () => {
    // Tests what happens when the manager component receives a response
    // from ajax requests.
    // This can either be the result of a search operation or as a
    // consequence of dis/associating resources to a tag.

    const component = {setState: jest.fn(async () => 23)};
    const manager = new DataManager(component);

    const response = {status: 200, json: jest.fn(async () => ({}))};

    // lets trigger an event with good status
    await manager.handleResponse(response);

    // we didnt specify any data, but thats OK, and we dont expect any errors
    expect(manager.component.setState.mock.calls).toEqual(
        [[{"data": undefined, "errors": {}}]]);

    // lets handle a response with some actual data
    response.json = jest.fn(async () => ({data: {foo: 'good', bar: 'stuff'}}));
    await manager.handleResponse(response);

    // and setState was called with some lovely data.
    expect(manager.component.setState.mock.calls[1]).toEqual(
        [{"data": {"bar": "stuff", "foo": "good"}, "errors": {}}]);
});


test('dataManager component', () => {

    class MockManager extends DataManager {

        get data () {
            return 7;
        }

        get errors () {
            return 23;
        }

        refreshData () {
            return '';
        }

        handleSubmit () {
            return '';
        }
    }

    class MockComponent extends React.PureComponent {

        render () {
            return <div>MOCKED</div>
        }
    }

    const ManagedComponent = dataManager(MockComponent, MockManager);
    const component = shallow(<ManagedComponent api={43} foo={43} bar={73} />);
    const manager = component.instance().manager;
    expect(manager instanceof MockManager).toBe(true);
    expect(manager.component).toBe(component.instance());

    const wrapped = component.find(MockComponent);
    expect(wrapped.length).toBe(1);
    expect(wrapped.props().manager).toBe(manager);
    expect(wrapped.props().refreshData).toBe(manager.refreshData);
    expect(wrapped.props().handleSubmit).toBe(manager.handleSubmit);
    expect(wrapped.props().data).toBe(7);
    expect(wrapped.props().errors).toBe(23);
    expect(wrapped.props().foo).toBe(43);
    expect(wrapped.props().bar).toBe(73);
});
