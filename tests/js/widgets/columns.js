import React from 'react';

import { shallow } from 'enzyme';

import { Columns, Container, Column } from 'widgets/columns';

test('Columns render', () => {
    const columndescriptors = [
        ['a', 2],
        ['b', 3],
        ['c', 7],
    ];
    const columns = shallow(<Columns columns={columndescriptors} />);
    const container = columns.find(Container);
    expect(container.length).toBe(1);
    expect(container.props().columns).toBe(3);
    expect(columns.props().ratios).toEqual([2, 3, 7]);
    expect(container.props().children.length).toBe(3);
    expect(container.props().children[0].props.children).toBe('a');
    expect(container.props().children[0].type).toBe(Column);
    expect(container.props().children[1].props.children).toBe('b');
    expect(container.props().children[1].type).toBe(Column);
    expect(container.props().children[2].props.children).toBe('c');
    expect(container.props().children[2].type).toBe(Column);
    expect(columns.text()).toBe('<Container />');
});

test('Column render', () => {
    let column = shallow(<Column />);
    expect(column.text()).toBe('');
    let div = column.find('div');
    expect(div.length).toBe(1);
    expect(div.props().className).toBe('column');
    column = shallow(<Column>xyz</Column>);
    expect(column.text()).toBe('xyz');
    column = shallow(<Column className='special-column'></Column>);
    div = column.find('div');
    expect(div.length).toBe(1);
    expect(div.props().className).toBe('column special-column');
});

test('Container render', () => {
    let container = shallow(<Container />);
    expect(container.text()).toBe('');
    expect(container.instance().columnStyles).toEqual([]);
    let div = container.find('div');
    expect(div.props().className).toBe('container');
    expect(div.props().style).toEqual({
        content: '',
        display: 'table',
        width: '100%',
    });
    expect(div.props().children).toEqual([]);
    container = shallow(<Container columns={3} />);
    expect(container.text()).toBe('');
    div = container.find('div');
    expect(container.instance().columnStyles).toEqual([
        {
            boxSizing: 'border-box',
            float: 'left',
            width: '33.333333333333336%',
        },
        {
            boxSizing: 'border-box',
            float: 'left',
            width: '33.333333333333336%',
        },
        {
            boxSizing: 'border-box',
            float: 'left',
            width: '33.333333333333336%',
        },
    ]);
    expect(div.props().children).toEqual([]);
    expect(div.props().style).toEqual({
        content: '',
        display: 'table',
        width: '100%',
    });
    expect(div.props().children).toEqual([]);
    container = shallow(<Container columns={3} ratios={[2, 3, 7]} />);
    expect(container.text()).toBe('');
    expect(container.instance().columnStyles).toEqual([
        {
            boxSizing: 'border-box',
            float: 'left',
            width: '16.666666666666664%',
        },
        { boxSizing: 'border-box', float: 'left', width: '25%' },
        {
            boxSizing: 'border-box',
            float: 'left',
            width: '58.333333333333336%',
        },
    ]);
});

test('Container render children', () => {
    const children = [<div key={1}>FOO...</div>, <div key={2}>...BAR</div>];
    const styles = jest.fn(() => {
        return [
            { background: 'black', color: 'red' },
            { background: 'green', color: 'gold' },
        ];
    });

    class MockContainer extends Container {
        get columnStyles() {
            return styles();
        }
    }

    const container = shallow(<MockContainer>{children}</MockContainer>);
    expect(container.text()).toBe('FOO......BAR');
    expect(styles.mock.calls).toEqual([[], [], [], []]);
    const div = container.find('div.container');
    expect(div.length).toBe(1);
    expect(div.props().children.length).toBe(2);
    const child0 = div.props().children[0];
    const child1 = div.props().children[1];
    expect(child0.props.style).toEqual({ background: 'black', color: 'red' });
    expect(child0.props.children).toEqual(children[0]);
    expect(child1.props.style).toEqual({ background: 'green', color: 'gold' });
    expect(child1.props.children).toEqual(children[1]);
});
