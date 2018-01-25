
import React from 'react';

import {ajax} from 'utils/ajax';
import TagResourceSearch from './search';
import TagResourceTable from './table';
import {ErrorList} from 'widgets/errors';

import "./tag-resources.css";


export default class TagResourceManager extends React.Component {

    constructor (props) {
        super(props);
        this.handleResponse = this.handleResponse.bind(this);
        this.handleSearchChange = this.handleSearchChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {type: 'assoc', search: "*", data: [], errors: {}};
    }

    async handleResponse (response) {
        const {status} = response;
        const json = await response.json();
        if (status === 200) {
            const {result} = json;
            return this.setState({data: result, errors: {}});
        }
        const {errors} = json;
        return this.setState({errors});
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
        return this.refreshData();
    }

    async handleSubmit (data) {
        let {search, type} = this.state;
        return this.handleResponse(
            await ajax.post(
                this.props.api,
                {type: type,
                 search: search,
                 paths: data}));
    }

    async refreshData () {
        let {search, type} = this.state;
        return this.handleResponse(
            await ajax.post(
                this.props.api,
                {type: type,
                 search: search}));
    }

    componentDidMount () {
        return this.refreshData();
    }

    render () {
        const {data, errors, type} = this.state;
        return (
            <div className="tag-resource-widget">
              <TagResourceSearch
                 handleSearchChange={this.handleSearchChange} />
              <ErrorList
                 errors={errors} />
              <TagResourceTable
                 data={data}
                 type={type}
                 handleSubmit={this.handleSubmit}  />
            </div>);
    }
}
