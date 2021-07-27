import { Localized } from '@fluent/react';
import { shallow } from 'enzyme';

/*
 * Taken from https://github.com/mozilla/addons-frontend/blob/58d1315409f1ad6dc9b979440794df44c1128455/tests/unit/helpers.js#L276
 * Maybe that ought to be put into a library?
 */

/*
 * Repeatedly render a component tree using enzyme.shallow() until
 * finding and rendering TargetComponent.
 *
 * This is useful for testing a component wrapped in one or more
 * HOCs (higher order components).
 *
 * The `componentInstance` parameter is a React component instance.
 * Example: <MyComponent {...props} />
 *
 * The `TargetComponent` parameter is the React class (or function) that
 * you want to retrieve from the component tree.
 */
export function shallowUntilTarget(
    componentInstance,
    TargetComponent,
    { maxTries = 10, shallowOptions = undefined, _shallow = shallow } = {},
) {
    if (!componentInstance) {
        throw new Error('componentInstance parameter is required');
    }
    if (!TargetComponent) {
        throw new Error('TargetComponent parameter is required');
    }

    let root = _shallow(componentInstance, shallowOptions);

    if (typeof root.type() === 'string') {
        // If type() is a string then it's a DOM Node.
        // If it were wrapped, it would be a React component.
        throw new Error(
            'Cannot unwrap this component because it is not wrapped',
        );
    }

    for (let tries = 1; tries <= maxTries; tries++) {
        if (root.is(TargetComponent)) {
            // Now that we found the target component, render it.
            return root.shallow(shallowOptions);
        }
        // Unwrap the next component in the hierarchy.
        root = root.dive();
    }

    throw new Error(`Could not find ${TargetComponent} in rendered
        instance: ${componentInstance}; gave up after ${maxTries} tries`);
}

/*
 * Wait until `ms` milliseconds have passed.
 *
 * Source: https://stackoverflow.com/questions/951021
 */
export function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

/*
 * Find Localized elements by their ID.
 *
 * Source: https://github.com/mozilla/testpilot/blob/93c9ea7aa6104fbbdc21508e44d486d7ca7c77aa/frontend/test/app/util.js
 */
export function findLocalizedById(wrapper, id) {
    return wrapper.findWhere(
        (elem) => elem.type() === Localized && elem.prop('id') === id,
    );
}

/*
 * Mock window.matchMedia, which is not implemented in JSDOM.
 *
 * Source: https://jestjs.io/docs/manual-mocks#mocking-methods-which-are-not-implemented-in-jsdom
 */
export function mockMatchMedia() {
    return Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation((query) => ({
            matches: false,
            media: query,
            onchange: null,
            addListener: jest.fn(), // deprecated
            removeListener: jest.fn(), // deprecated
            addEventListener: jest.fn(),
            removeEventListener: jest.fn(),
            dispatchEvent: jest.fn(),
        })),
    });
}
