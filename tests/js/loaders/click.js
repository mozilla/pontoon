
import {Loader, ClickLoader} from 'loaders';


test('ClickLoader constructor', () => {
    const loader = new ClickLoader();
    expect(loader instanceof Loader).toBe(true);
    expect(loader.event).toBe('click');
})


test('ClickLoader isActive', () => {
    // Tests that clickloader always returns false for isActive as this
    // method should be added in descendant classes if required.

    const loader = new ClickLoader();
    expect(loader.isActive()).toBe(false);
    expect(loader.isActive('FOO')).toBe(false);
})


test('ClickLoader handle', () => {
    // Tests that handle mounts the correct components in response to events
    // on the correct nodes

    class MockLoader extends ClickLoader {

        get nodes () {
            return [7, 13, 23];
        }
    }

    const loader = new MockLoader();
    loader.mountComponent = jest.fn()

    // fire an event, but with a "node" that is not in this.nodes
    const evt = {preventDefault: jest.fn(), target: 'x'}
    loader.handle(evt);

    // nothing called
    expect(loader.mountComponent.mock.calls).toEqual([])
    expect(evt.preventDefault.mock.calls).toEqual([])

    // this time, fire an event with a "node" in this.nodes
    evt.target = 13
    loader.handle(evt);

    // evt.preventDefault and this.mountComponent were called
    expect(evt.preventDefault.mock.calls).toEqual([[]])
    expect(loader.mountComponent.mock.calls).toEqual([[13]])
})


test('ClickLoader loadActive', () => {
    // Tests that loadActive - which is called after first load,
    // if any of the nodes are deemed to be "active", clicks the node

    const loader = new ClickLoader();
    const node = {click: jest.fn()}
    loader.loadActive(node);
    expect(node.click.mock.calls).toEqual([[]]);
})


test('ClickLoader load', () => {
    // Tests that load adds the correct event listeners and that mountComponent
    // is not called. Also checks that if any "node" is active this.loadActive
    // is called with it

    class MockLoader extends ClickLoader {

        get nodes () {
            return [7, 13, 23];
        }
    }

    const loader = new MockLoader();

    document.addEventListener = jest.fn()
    loader.mountComponent = jest.fn()
    loader.isActive = jest.fn((node) => node === 23)
    loader.loadActive = jest.fn()
    loader.load()

    // event was added
    expect(document.addEventListener.mock.calls).toEqual(
        [['click', loader.handle]])

    // mountComponent was not called
    expect(loader.mountComponent.mock.calls).toEqual([])

    // isActive was called with each node
    expect(loader.isActive.mock.calls).toEqual(
        [[7], [13], [23]])

    // loadActive was called with the active node
    expect(loader.loadActive.mock.calls).toEqual([[23]])
})
