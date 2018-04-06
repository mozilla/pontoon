
import React from 'react';

import {getComponents} from 'utils/components';


export default class DropdownMenuButton extends React.Component {
    state = {open: false};

    handleClick = () => {
        this.setState((prevState) => ({open: !prevState.open}));
    }

    handleClose = (evt) => {
        if (!(this.buttonNode && this.buttonNode.contains(evt.target))) {
            this.setState({open: false});
        }
    }

    refNode = (node) => {
        this.buttonNode = node;
    }

    render () {
        const {buttonProps, className, components, id, menuProps, ...props} = this.props;
        const {button, menu} = getComponents(this);
        return (
            <div id={id} className={className}>
              {this.renderButton(button, buttonProps, props)}
              {this.renderMenu(menu, menuProps, props)}
            </div>);
    }

    renderButton (Button, buttonProps, props) {
        return (
            <div
               className="button selector"
               onClick={this.handleClick}
               key={0}
               ref={this.refNode}>
              <Button {...props} {...buttonProps} />
            </div>);
    }

    renderMenu (Menu, menuProps, props) {
        const {open} = this.state;
        if (!open) {
            return '';
        }
        return (
            <Menu
               handleClose={this.handleClose}
               key={1}
               {...props}
               {...menuProps} />);
    }
}
