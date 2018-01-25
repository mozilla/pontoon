
import React from 'react';

import {Columns} from 'widgets/columns';


export default class TagResourceSearch extends Columns {

    get columns () {
        return [[this.renderSearchInput(), 3],
                [this.renderSearchSelect(), 2]];
    }

    renderSearchInput () {
        return (
            <input
               type="text"
               className="search-tag-resources"
               onChange={this.props.handleSearchChange}
               placeholder="Search for resources" />);
    }

    renderSearchSelect () {
        return (
            <select
               className="search-tag-resource-type"
               onChange={this.props.handleSearchChange}>
              <option value="assoc">Linked</option>
              <option value="nonassoc">Not linked</option>
            </select>);
    }
}
