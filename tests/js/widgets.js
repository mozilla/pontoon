
import React from 'react';

import {mount, shallow} from 'enzyme';

import {Columns, Container, Column} from 'widgets/columns';
import Checkbox from 'widgets/checkbox';
import {ErrorList, Error} from 'widgets/errors';


test('Error render', () => {
    let error = shallow(<Error name='FOO' error='BAR' />);
    expect(error.text()).toBe("FOO: BAR");
    let li = error.find('li.error');
    expect(li.length).toBe(1);
});


test('ErrorList render', () => {
    let errors = shallow(<ErrorList errors={{}} />);
    expect(errors.text()).toBe("");
    expect(errors.find('ul').length).toBe(0);
    errors = shallow(<ErrorList errors={{foo: 'Did a foo', bar: 'Bars happen'}} />);
    let ul = errors.find('ul.errors');
    expect(ul.length).toBe(1);
    let lis = ul.find(Error);
    expect(lis.length).toBe(2);
    expect(errors.text()).toBe("<Error /><Error />");
});


test('Checkbox render', () => {
    let checkbox = shallow(<Checkbox />);
    expect(checkbox.text()).toBe('');
    expect(checkbox.instance().el.indeterminate).toBe(false);

    checkbox = shallow(<Checkbox indeterminate="true" />);
    expect(checkbox.text()).toBe('');
    expect(checkbox.instance().el.indeterminate).toBe(true);
    expect(checkbox.instance().el.nodeName).toBe(undefined);

    checkbox = mount(<Checkbox />);
    // this time el is an HTML node
    expect(checkbox.instance().el.indeterminate).toBe(false);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');

    checkbox = mount(<Checkbox indeterminate={true} />);
    expect(checkbox.instance().el.indeterminate).toBe(true);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');

    let prevProp = checkbox.props();
    checkbox.setProps({indeterminate: false});
    checkbox.instance().componentDidUpdate(prevProp);
    expect(checkbox.instance().el.indeterminate).toBe(false);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');

    prevProp = checkbox.props();
    checkbox.setProps({indeterminate: true});
    checkbox.instance().componentDidUpdate(prevProp);
    expect(checkbox.instance().el.indeterminate).toBe(true);
    expect(checkbox.instance().el.nodeName).toEqual('INPUT');
});


test('Columns render', () => {

    class MockColumns extends Columns {

        get columns () {
            return [['a', 2], ['b', 3], ['c', 7]];
        }
    }

    const columns = shallow(<MockColumns />);
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
    expect(div.props().style).toEqual(
        {"content": "", "display": "table", "width": "100%"});
    expect(div.props().children).toEqual([]);
    container = shallow(<Container columns={3} />);
    expect(container.text()).toBe('');
    div = container.find('div');
    expect(container.instance().columnStyles).toEqual(
        [{"boxSizing": "border-box", "float": "left", "overflow": "hidden", "width": "33.333333333333336%"},
         {"boxSizing": "border-box", "float": "left", "overflow": "hidden", "width": "33.333333333333336%"},
         {"boxSizing": "border-box", "float": "left", "overflow": "hidden", "width": "33.333333333333336%"}]);
    expect(div.props().children).toEqual([]);
    expect(div.props().style).toEqual(
        {"content": "", "display": "table", "width": "100%"});
    expect(div.props().children).toEqual([]);
    container = shallow(<Container columns={3} ratios={[2, 3, 7]} />);
    expect(container.text()).toBe('');
    expect(container.instance().columnStyles).toEqual(
        [{"boxSizing": "border-box", "float": "left", "overflow": "hidden", "width": "16.666666666666664%"},
         {"boxSizing": "border-box", "float": "left", "overflow": "hidden", "width": "25%"},
         {"boxSizing": "border-box", "float": "left", "overflow": "hidden", "width": "58.333333333333336%"}]);
});


test('Container render children', () => {
    const children = [<div>FOO...</div>, <div>...BAR</div>];
    const styles = jest.fn(() => {
        return [
            {background: 'black', color: 'red'},
            {background: 'green', color: 'gold'}];
    });

    class MockContainer extends Container {

        get columnStyles () {
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
    expect(child0.props.style).toEqual(
        {background: 'black', color: 'red'});
    expect(child0.props.children).toEqual(children[0]);
    expect(child1.props.style).toEqual(
        {background: 'green', color: 'gold'});
    expect(child1.props.children).toEqual(children[1]);
});
