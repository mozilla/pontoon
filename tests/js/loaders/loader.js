
import ReactDOM from 'react-dom';
import React from 'react';

import {Loader} from 'loaders';
import {NotImplementedError} from 'errors';


test('Loader constructor', () => {
    const loader = new Loader();

    // component and selector *must* be set on descendant classes
    expect(() => {
        loader.component
    }).toThrow(NotImplementedError);
    expect(() => {
        loader.selector
    }).toThrow(NotImplementedError);
    expect(() => {
        loader.nodes
    }).toThrow(NotImplementedError);

    // getting props and the node to render to can be overridden
    // but return {} and the trigger node respectively by default
    expect(loader.getProps('FOO')).toEqual({});
    expect(loader.getRenderNode('BAR')).toBe('BAR');
})


test('Loader nodes', () => {
    // tests that nodes are found by querying the dom with this.selector

    class MockLoader extends Loader {

        get selector () {
            return 7;
        }
    }

    const loader = new MockLoader();
    document.querySelectorAll = jest.fn(() => [1, 2, 3])
    expect(loader.nodes).toEqual([1, 2, 3]);
    expect(document.querySelectorAll.mock.calls).toEqual([[7]]);
})


test('Loader load', () => {
    // Tests that when load is called mountComponent is called with each
    // of the found nodes.

    class MockLoader extends Loader {

        get nodes () {
            return ['a', 'b', 'c']
        }
    }

    const loader = new MockLoader();
    loader.mountComponent = jest.fn()
    loader.load()
    expect(loader.mountComponent.mock.calls.map(x => x[0])).toEqual(['a', 'b', 'c']);
})


test('Loader mountComponent', () => {
    // Tests that ReactDOM.render is called with the correct component and target node.
    // Also ensures that the node is unmounted and emptied before loading

    class MockComponent extends React.PureComponent {
        render () {
            return (<div>MOCK</div>);
        }
    }

    class MockLoader extends Loader {

        get component () {
            return MockComponent
        }
    }

    const loader = new MockLoader();
    loader.getRenderNode = jest.fn(() => ({innerHTML: 'REMOVEME'}))
    loader.getProps = jest.fn(() => ({FOO: 2, BAR: 3}))
    loader.unmountComponent = jest.fn()
    ReactDOM.render = jest.fn()

    loader.mountComponent('X');

    // any existing components should be unmounted
    expect(loader.unmountComponent.mock.calls).toEqual([['X']])

    // getRenderNode is called to get correct target node
    expect(loader.getRenderNode.mock.calls).toEqual([['X']]);

    // getProps was called with the node
    expect(loader.getProps.mock.calls).toEqual([['X']]);

    // ReactDOM.render was called with the component and the target node
    // emptied of HTML
    expect(ReactDOM.render.mock.calls).toEqual(
        [[<MockComponent FOO={2} BAR={3} />, {"innerHTML": ""}]])
})


test('Loader unmountComponent', () => {
    // Tests that ReactDOM.unmountComponentAtNode is called with the correct target
    // node.

    const loader = new Loader();
    loader.getRenderNode = jest.fn(() => 23);
    ReactDOM.unmountComponentAtNode = jest.fn();

    loader.unmountComponent(7);

    // getRenderNode was called
    expect(loader.getRenderNode.mock.calls).toEqual([[7]])
    expect(ReactDOM.unmountComponentAtNode.mock.calls).toEqual([[23]])
})
