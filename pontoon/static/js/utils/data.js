
import React from 'react';

import {ajax} from 'utils/ajax';


export class DataManager {

    constructor (component) {
        this.component = component;
        this.handleResponse = this.handleResponse.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.refreshData = this.refreshData.bind(this);
    }

    get data () {
        const {data} = this.component.state;
        return data;
    }

    get errors () {
        const {errors} = this.component.state;
        return errors;
    }

    get api () {
        return this.component.props.api;
    }

    get requestMethod () {
        return this.component.props.requestMethod || 'get';
    }

    get submitMethod () {
        return this.component.props.submitMethod || this.requestMethod;
    }

    async refreshData (params) {
        return this.handleResponse(
            await ajax[this.requestMethod](this.api, params));
    }

    async handleResponse (response) {
        const {status} = response;
        const json = await response.json();
        if (status === 200) {
            const {data} = json;
            this.component.setState({data, errors: {}});
            return;
        }
        const {errors} = json;
        this.component.setState({errors});
    }

    async handleSubmit (params) {
        return this.handleResponse(
            await ajax[this.submitMethod](this.api, params));
    }
}


export function dataManager(WrappedComponent, Manager, data) {

    return class Wrapper extends React.Component {

        constructor(props) {
            super(props);
            Manager = Manager || DataManager;
            this.manager = new Manager(this);
            this.state = {errors: {}, data: data || []};
        }

        render() {
            return (
                <WrappedComponent
                   manager={this.manager}
                   errors={this.manager.errors}
                   data={this.manager.data}
                   handleSubmit={this.manager.handleSubmit}
                   refreshData={this.manager.refreshData}
                   {...this.props} />);
        }
    };
}
