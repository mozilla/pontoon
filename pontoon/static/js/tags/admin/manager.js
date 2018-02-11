
import React from 'react';

import TagResourceSearch from './search';
import TagResourceTable from './table';
import {ErrorList} from 'widgets/errors';

import "./tag-resources.css";

import {DataManager, dataManager} from 'utils/data';


export class TagResourceManagerWidget extends React.Component {

    constructor (props) {
        super(props);
        this.handleSearchChange = this.handleSearchChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {type: 'assoc', search: "*"};
    }

    componentDidMount () {
        return this.props.refreshData({...this.state});
    }

    async handleSearchChange (evt) {
        switch (evt.target.nodeName) {
        case 'INPUT':
            await this.setState({search: evt.target.value});
            break;
        case 'SELECT':
            await this.setState({type: evt.target.value});
            break;
        }
        return this.props.refreshData({...this.state});
    }

    handleSubmit (checked) {
        return this.props.handleSubmit(
            Object.assign({}, {...this.state}, checked));
    }

    render () {
        const {data, errors} = this.props;
        const {type} = this.state;
        return (
            <div className="tag-resource-widget">
              <TagResourceSearch
                 handleSearchChange={this.handleSearchChange} />
              <ErrorList
                 errors={errors || {}} />
              <TagResourceTable
                 data={data || []}
                 type={type}
                 handleSubmit={this.handleSubmit}  />
            </div>);
    }
}


export class TagResourceDataManager extends DataManager {

    get requestMethod () {
        return 'post';
    }

}

export const TagResourceManager = dataManager(TagResourceManagerWidget, TagResourceDataManager);
