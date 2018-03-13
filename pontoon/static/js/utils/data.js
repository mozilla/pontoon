
import React from 'react';

import {ajax} from 'utils/ajax';


export class DataManager {

    constructor (component) {
        this.component = component;
    }

    get data () {
        return this.component.state.data;
    }

    get errors () {
        return this.component.state.errors;
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

    refreshData = async (params) => {
        return this.handleResponse(
            await ajax.fetch(
                this.api,
                params,
                {method: this.requestMethod}));
    }

    handleResponse = async (response) => {
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

    handleSubmit = async (params) => {
        return this.handleResponse(
            await ajax.fetch(
                this.api,
                params,
                {method: this.requestMethod}));
    }
}


export function dataManager(WrappedComponent, Manager, data) {

    return class Wrapper extends React.Component {

        constructor(props) {
            super(props);
            Manager = Manager || DataManager;
            this.manager = new Manager(this);
            this.state = {errors: {}, data: data};
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
