

import React from 'react';

import {mount, shallow} from 'enzyme';

import {getCSRFToken} from 'utils/csrf';
import {Form, CSRFToken, SignoutForm} from 'widgets/forms';

jest.mock('utils/csrf');


test('Form render', () => {
    let form = shallow(<Form />);
    expect(form.props()).toEqual(
        {action: '',
         children: [<CSRFToken />, undefined],
         method: "POST"});
    form = shallow(
        <Form
           action="/somewhere/else"
           foo={7}
           bar={23}>
          BAZ
        </Form>);
    expect(form.props()).toEqual(
        {action: '/somewhere/else',
         foo: 7,
         bar: 23,
         children: [<CSRFToken />, 'BAZ'],
         method: "POST"});
});


test('Form mount', () => {
    class MockForm extends Form {

        renderCSRF () {
            return 'CSRF';
        }
    }

    let form = mount(<MockForm />);
    expect(form.find('form').getElement().ref).toBe(
        form.instance().handleFormLoad);
});


test('Form handleFormLoad', () => {

    let form = shallow(<Form />);
    form.instance().handleFormLoad();

    const handleFormLoad = jest.fn();
    form = shallow(<Form handleFormLoad={handleFormLoad} />);

    form.instance().handleFormLoad(23);
    expect(handleFormLoad.mock.calls).toEqual([[23]]);
});


test('SignoutForm render', () => {
    let form = shallow(<SignoutForm />);
    expect(form.text()).toEqual('<Form />');
    expect(form.props()).toEqual(
        {action: "/accounts/logout/?next=/at/all",
         className: "csrf",
         style: {"display": "none"}});
    form = shallow(
        <SignoutForm
           foo={7}
           action="/nowhere"
           className="other"
           />);
    expect(form.props()).toEqual(
        {action: "/nowhere",
         className: "other",
         foo: 7,
         style: {"display": "none"}});
});


test('CSRFToken render', () => {
    getCSRFToken.mockImplementation(() => 23);

    let token = shallow(<CSRFToken />);
    expect(token.text()).toEqual('');
    let input = token.find('input');
    expect(input.props()).toEqual(
        {name: "csrfmiddlewaretoken",
         type: "hidden",
         value: 23});
});
