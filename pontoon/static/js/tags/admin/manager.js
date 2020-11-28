import React from 'react';

import TagResourceSearch from './search';
import TagResourceTable from './table';
import { ErrorList } from 'widgets/errors';

import './tag-resources.css';

import { dataManager } from 'utils/data';

export class TagResourceManagerWidget extends React.Component {
    state = { type: 'assoc', search: '' };

    componentDidMount() {
        this.props.refreshData({ ...this.state });
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevState !== this.state) {
            this.props.refreshData({ ...this.state });
        }
    }

    handleSearchChange = (change) => {
        this.setState(change);
    };

    handleSubmit = (checked) => {
        return this.props.handleSubmit(Object.assign({}, this.state, checked));
    };

    render() {
        const { data, errors } = this.props;
        const { type } = this.state;
        return (
            <div className='tag-resource-widget'>
                <TagResourceSearch
                    handleSearchChange={this.handleSearchChange}
                />
                <ErrorList errors={errors || {}} />
                <TagResourceTable
                    data={data || []}
                    type={type}
                    handleSubmit={this.handleSubmit}
                />
            </div>
        );
    }
}

export const TagResourceManager = dataManager(TagResourceManagerWidget);
