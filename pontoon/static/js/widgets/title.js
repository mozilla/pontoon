

import React from 'react';


export class Title extends React.PureComponent {

    render () {
        if (!this.props.title) {
            return '';
        }
        return (
            <h1 className={this.props.className}>
              {this.renderTitle()}
              {this.renderSubtitle()}
            </h1>);
    }

    renderSubtitle () {
        if (!this.props.subtitle) {
            return '';
        }
        return (
            <a href={this.props.href || "#"} className="small">
              {this.props.subtitle}
            </a>);
    }

    renderTitle () {
        return (
            <a href={this.props.href || "#"}>
              {this.props.title}
            </a>);
    }
}
