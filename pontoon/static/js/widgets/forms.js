
import React from 'react';

import {getCSRFToken} from 'utils/csrf';


export class CSRFToken extends React.PureComponent {

    render () {
        return (
            <input
               value={this.props.csrf || getCSRFToken()}
               name="csrfmiddlewaretoken"
               type="hidden" />);
    }
}


export class Form extends React.PureComponent {

    handleFormLoad = (form) => {
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
              <CSRFToken />
              {children}
            </form>);
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
