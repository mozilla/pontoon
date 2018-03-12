
import React from 'react';


export default class DropdownMenuButton extends React.Component {

    constructor (props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.refNode = this.refNode.bind(this);
        this.state = {open: false};
    }

    handleClick () {
        this.setState((prevState) => ({open: !prevState.open}));
    }

    handleClose (evt) {
        if (this.buttonNode && this.buttonNode.contains(evt.target)) {
            return;
        }
        this.setState({open: false});
    }

    refNode (node) {
        this.buttonNode = node;
    }

    render () {
        const {id, className} = this.props;
        return (
            <div id={id} className={className}>
              {this.renderButton()}
              {this.renderMenu()}
            </div>);
    }

    renderButton () {
        const {buttonProps, components, menuProps, ...props} = this.props;
        const {button: Button} = components;
        return (
            <div
               className="button selector"
               onClick={this.handleClick}
               ref={this.refNode}>
              <Button {...props} {...buttonProps} />
            </div>);
    }

    renderMenu () {
        const {open} = this.state;
        if (!open) {
            return '';
        }
        const {buttonProps, components, menuProps, ...props} = this.props;
        const {menu: Menu} = components;
        return <Menu handleClose={this.handleClose} {...props} {...menuProps} />;
    }
}
