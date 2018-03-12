
import React from 'react';

import {PontoonCSRF} from 'utils/csrf';


export class CSRFToken extends React.PureComponent {

    get csrf () {
        return new PontoonCSRF().value;
    }

    render () {
        return (
            <input
               value={this.csrf}
               name="csrfmiddlewaretoken"
               type="hidden" />);
    }
}


export class Form extends React.PureComponent {

    constructor (props) {
        super(props);
        this.handleFormLoad = this.handleFormLoad.bind(this);
    }

    handleFormLoad (form) {
        if (this.props.handleFormLoad) {
            this.props.handleFormLoad(form);
        }
    }

    render () {
        const {action, children, method, ...props} = this.props;
        return (
            <form
               method={method || "POST"}
               ref={this.handleFormLoad}
               action={this.props.action || ''}
               {...props}>
              {this.renderCSRF()}
              {children}
            </form>);
    }

    renderCSRF () {
        return <CSRFToken />;
    }
}


export class SignoutForm extends React.PureComponent {

    get action () {
        return "/accounts/logout/?next=" + this.redirectURL;
    }

    get redirectURL() {
        return window.location.pathname + window.location.search;
    }

    render () {
        return (
            <Form
               style={{display: "none"}}
               action={this.action}
               className="csrf"
               {...this.props}
               />);
    }
}
