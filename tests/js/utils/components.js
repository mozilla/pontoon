

import React from 'react';

import {shallow} from 'enzyme';

import {componentManager} from 'utils/components';


test('componentManager component', () => {

    class MockComponent extends React.PureComponent {

        render () {
            return <div>MOCKED</div>
        }
    }

    const ManagedComponent = componentManager(MockComponent, {bar: 43, baz: 73});
    const component = shallow(<ManagedComponent components={{foo: 7, bar: 23}} />);

    expect(component.props().components).toEqual({"bar": 43, "baz": 73, "foo": 7})
});
