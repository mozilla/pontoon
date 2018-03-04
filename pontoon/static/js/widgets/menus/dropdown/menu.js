
import React from 'react';

import {getComponents} from 'utils/components';
import {List} from 'widgets/lists/generic';

import MenuItem from './item';
import './menu.css';


export default class DropdownMenu extends React.PureComponent {
    components = {item: MenuItem};

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

    handleClickOutside = (evt) => {
        if (this.node && !this.node.contains(evt.target) && this.props.handleClose) {
            this.props.handleClose(evt);
        }
    }

    render () {
        return (
            <div ref={n => this.node = n}>
              <List
                 items={this.items}
                 components={getComponents(this)}
                 className="menu dropdown" />
            </div>);
    }
}
