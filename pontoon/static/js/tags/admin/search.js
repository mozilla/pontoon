import React from 'react';

import { Columns } from 'widgets/columns';

export default class TagResourceSearch extends React.PureComponent {
    get columns() {
        return [
            [this.renderSearchInput(), 3],
            [this.renderSearchSelect(), 2],
        ];
    }

    handleChange = (evt) => {
        return this.props.handleSearchChange({
            [evt.target.name]: evt.target.value,
        });
    };

    renderSearchInput() {
        return (
            <input
                type='text'
                className='search-tag-resources'
                name='search'
                onChange={this.handleChange}
                placeholder='Search for resources'
            />
        );
    }

    renderSearchSelect() {
        return (
            <select
                className='search-tag-resource-type'
                name='type'
                onChange={this.handleChange}
            >
                <option value='assoc'>Linked</option>
                <option value='nonassoc'>Not linked</option>
            </select>
        );
    }

    render() {
        return <Columns columns={this.columns} />;
    }
}
