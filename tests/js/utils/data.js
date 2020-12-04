import React from 'react';

import { shallow } from 'enzyme';

import { ajax } from 'utils/ajax';

import { DataManager, dataManager } from 'utils/data';

class MockComponent extends React.PureComponent {
    render() {
        return <div />;
    }
}

test('DataManager constructor', () => {
    const Manager = dataManager(MockComponent);
    const manager = shallow(<Manager />);
    expect(manager.state()).toEqual({ data: undefined, errors: {} });
    expect(manager.instance().requestMethod).toBe('get');
    expect(manager.instance().submitMethod).toBe('get');
});

test('DataManager requestMethod', () => {
    // requestMethod can be overriden in props
    const Manager = dataManager(MockComponent);
    const manager = shallow(<Manager requestMethod={23} />);
    expect(manager.instance().requestMethod).toBe(23);
    expect(manager.instance().submitMethod).toBe(23);
});

test('DataManager submitMethod', () => {
    // submitMethod can be overriden in props
    const Manager = dataManager(MockComponent);
    const manager = shallow(<Manager submitMethod={7} />);
    expect(manager.instance().requestMethod).toBe('get');
    expect(manager.instance().submitMethod).toBe(7);
});

test('DataManager refreshData', async () => {
    // refreshData calls ajax and gives the child components a shakedown
    // with the results. Its called in componentDidMount as well as in
    // response to user actions.

    const Manager = dataManager(MockComponent);
    const manager = shallow(<Manager api={43} />);
    manager.instance().handleResponse = jest.fn(async () => 23);
    ajax.get = jest.fn(async () => 37);
    let result = await manager.instance().refreshData({ foo: 'BAR' });

    // we get back the Promise of a handled Response.
    expect(result).toBe(23);

    // handleResponse was called with the awaited content from ajax.get
    expect(manager.instance().handleResponse.mock.calls).toEqual([[37]]);

    // and ajax.get was called with the expected vars
    expect(ajax.get.mock.calls).toEqual([
        [43, { foo: 'BAR' }, { method: 'get' }],
    ]);
});

test('DataManager handleSubmit', async () => {
    // Tests what happens when user clicks handleSubmit

    const Manager = dataManager(MockComponent);
    const manager = shallow(<Manager api={43} submitMethod='post' />);

    const response = { json: async () => '113' };
    ajax.post = jest.fn(async () => response);

    manager.instance().handleResponse = jest.fn(async () => 23);

    // ajax gets fired from componentDidMount, so lets clear it
    ajax.post.mockClear();

    let result = await manager.instance().handleSubmit(7);

    // we expect the async response from handleResponse to be returned
    expect(result).toBe(23);

    // handleResponse gets called with the Promise of some json from ajax
    expect(manager.instance().handleResponse.mock.calls).toEqual([[response]]);

    // and ajax got called with all of the expected post data.
    expect(ajax.post.mock.calls).toEqual([[43, 7, { method: 'post' }]]);
});

test('DataManager handleResponse errors', async () => {
    // Tests error handling in the ResourceManager widget

    const Manager = dataManager(MockComponent);
    const manager = shallow(<Manager requestMethod={23} />);

    manager.instance().setState = jest.fn(() => 23);

    // trigger handleResponse with bad status
    const response = { status: 500, json: jest.fn(async () => ({})) };
    await manager.instance().handleResponse(response);

    // setState was called with our errors, which we didnt specify, but thats ok.
    expect(manager.instance().setState.mock.calls).toEqual([
        [{ errors: undefined }],
    ]);

    // lets see what happens when we specify errors.
    response.json = jest.fn(async () => ({
        errors: { foo: 'bad', bar: 'stuff' },
    }));
    await manager.instance().handleResponse(response);

    // but this time setState was called with the errors
    expect(manager.instance().setState.mock.calls[1]).toEqual([
        { errors: { bar: 'stuff', foo: 'bad' } },
    ]);
});

test('DataManager handleResponse', async () => {
    // Tests what happens when the manager component receives a response
    // from ajax requests.
    // This can either be the result of a search operation or as a
    // consequence of dis/associating resources to a tag.

    const Manager = dataManager(MockComponent);
    const manager = shallow(<Manager requestMethod={23} />);

    manager.instance().setState = jest.fn(() => 23);

    // lets trigger an event with good status
    const response = { status: 200, json: jest.fn(async () => ({})) };
    await manager.instance().handleResponse(response);

    // we didnt specify any data, but thats OK, and we dont expect any errors
    expect(manager.instance().setState.mock.calls).toEqual([
        [{ data: undefined, errors: {} }],
    ]);

    // lets handle a response with some actual data
    response.json = jest.fn(async () => ({
        data: { foo: 'good', bar: 'stuff' },
    }));
    await manager.instance().handleResponse(response);

    // and setState was called with some lovely data.
    expect(manager.instance().setState.mock.calls[1]).toEqual([
        { data: { bar: 'stuff', foo: 'good' }, errors: {} },
    ]);
});

test('dataManager component', () => {
    class MockManager extends DataManager {
        get data() {
            return 7;
        }

        get errors() {
            return 23;
        }
    }

    const Manager = dataManager(MockComponent, MockManager);
    const manager = shallow(<Manager api={43} foo={43} bar={73} />);
    const wrapped = manager.find(MockComponent);
    expect(wrapped.length).toBe(1);
    expect(wrapped.props().manager).toEqual(new MockManager(manager.state()));
    expect(wrapped.props().refreshData).toBe(manager.instance().refreshData);
    expect(wrapped.props().handleSubmit).toBe(manager.instance().handleSubmit);
    expect(wrapped.props().data).toBe(7);
    expect(wrapped.props().errors).toBe(23);
    expect(wrapped.props().foo).toBe(43);
    expect(wrapped.props().bar).toBe(73);
});
