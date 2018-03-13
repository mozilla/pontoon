
import React from 'react';


export class Icon extends React.PureComponent {

    get className () {
        let className = this.props.className ? ' ' + this.props.className : '';
        return "icon fa fa-" + this.props.name + " fa-fw" + className;
    }

    render () {
        if (!this.props.name) {
            return '';
        }
        return <i className={this.className}></i>;
    }
}


export class IconLink extends React.PureComponent {

    render () {
        const {children, icon, href, ...props} = this.props;
        if (!icon) {
            return '';
        }
        return (
            <a href={href} {...props}>
              <Icon name={icon} />
              {children}
            </a>);
    }
}
