
import React from 'react';

import {Icon} from 'widgets/icons';

import './search.css';


export class SearchControls extends React.PureComponent {

    constructor (props) {
        super(props);
        this.handleFilterChange = this.handleFilterChange.bind(this);
    }

    handleFilterChange (evt) {
        if (this.props.handleFilterChange) {
            return this.props.handleFilterChange(evt.target.value);
        }
    }

    render () {
        return (
            <menu className="controls">
              <div className="search-wrapper small clearfix">
                <Icon name="search" />
                <input
                   onChange={this.handleFilterChange}
                   className="table-filter"
                   autoComplete="off"
                   autoFocus="off"
                   placeholder={this.props.placeholder}
                   type="search"
                   />
              </div>
            </menu>);
    }
}
