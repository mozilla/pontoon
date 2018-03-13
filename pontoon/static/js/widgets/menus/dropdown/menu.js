
import React from 'react';

import {List} from 'widgets/lists/generic';

import MenuItem from './item'

import './menu.css';


export default class DropdownMenu extends React.PureComponent {

    constructor(props) {
        super(props);
        this.handleClickOutside = this.handleClickOutside.bind(this);
    }

    get components () {
        const components = {item: MenuItem};
        return Object.assign({}, components, (this.props.components || {}));
    }

    get items () {
        return this.props.items.map(item => {
            return {value: item};
        });
    }

    componentDidMount() {
        document.addEventListener('mousedown', this.handleClickOutside);
    }

    componentWillUnmount() {
        document.removeEventListener('mousedown', this.handleClickOutside);
    }

    handleClickOutside (evt) {
        if (this.node && !this.node.contains(evt.target) && this.props.handleClose) {
            this.props.handleClose(evt);
        }
    }

    render () {
        return (
            <div ref={n => this.node = n}>
              <List
                 items={this.items}
                 components={this.components}
                 className="menu dropdown" />
            </div>);
    }
}
