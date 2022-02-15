import React from 'react';

import './errors.css';

export class Error extends React.PureComponent {
    get className() {
        return 'error';
    }

    render() {
        let { className, error, name, ...props } = this.props;
        className = className
            ? className + ' ' + this.className
            : this.className;
        return (
            <li className={className} {...props}>
                {name}: {error}
            </li>
        );
    }
}

export class ErrorList extends React.PureComponent {
    get className() {
        return 'errors';
    }

    get errorComponent() {
        return Error;
    }

    renderError(key, name, error) {
        const ErrorComponent = this.errorComponent;
        return <ErrorComponent error={error} key={key} name={name} />;
    }

    render() {
        let { errors, className, ...props } = this.props;
        className = className
            ? className + ' ' + this.className
            : this.className;
        if (!Object.keys(errors).length) {
            return '';
        }
        return (
            <ul className={className} {...props}>
                {Object.entries(errors).map(([name, error], key) => {
                    return this.renderError(key, name, error);
                })}
            </ul>
        );
    }
}
