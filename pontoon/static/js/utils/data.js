
import React from 'react';

import NProgress from 'nprogress';
import 'nprogress/nprogress.css';

import {ajax} from 'utils/ajax';


export class DataManager {

    constructor (state) {
        this.state = state;
    }

    get content () {
        return {};
    }

    get data () {
        return this.state.data;
    }

    get errors () {
        return this.state.errors;
    }
}


export function dataManager(WrappedComponent, Manager, data) {

    return class Wrapper extends React.Component {
        state = {errors: {}, data: data, params: {}};

        get api () {
            return this.props.api;
        }

        get requestMethod () {
            return this.props.requestMethod || 'get';
        }

        get submitMethod () {
            return this.props.submitMethod || this.requestMethod;
        }

        refreshData = async (params) => {
            if (this.props.updateParams) {
                this.props.updateParams(params);
            }
            if (this.props.onRefresh) {
                this.props.onRefresh();
            }
            return this.handleResponse(
                await ajax.fetch(
                    this.api,
                    params,
                    {method: this.requestMethod}));
        }

        handleResponse = async (response) => {
            const {status} = response;
            const json = await response.json();
            if (this.props.onResponse) {
                this.props.onResponse();
            }
            if (status === 200) {
                const {data} = json;
                this.setState(prevState => {
                    if (Array.isArray(data)) {
                        return {data: data, errors: {}}
                    }
                    return {data: Object.assign(prevState.data || {}, {...data}),
                            errors: {}}});
                return;
            }
            const {errors} = json;
            this.setState({errors});
        }

        handleSubmit = async (params) => {
            return this.handleResponse(
                await ajax.fetch(
                    this.api,
                    params,
                    {method: this.submitMethod}));
        }

        render() {
            Manager = Manager || DataManager;
            const manager = new Manager(this.state);
            return (
                <WrappedComponent
                   manager={manager}
                   content={manager.content}
                   errors={manager.errors}
                   data={manager.data}
                   handleSubmit={this.handleSubmit}
                   refreshData={this.refreshData}
                   {...this.props} />);
        }
    };
}


export const progressiveDataManager = (WrappedComponent, Manager, data) => {

    return class Wrapper extends React.Component {

        handleRefresh = () => {
            NProgress.start();
        }

        handleResponse = () => {
            NProgress.done();
        }

        render () {
            const Component = dataManager(WrappedComponent, Manager, data);
            return (
                <Component
                   onRefresh={this.handleRefresh}
                   onResponse={this.handleResponse}
                   {...this.props} />);
        }
    };
};


export function Loading(props) {
    if (props.error) {
        return <div>Error!</div>;
    } else if (props.pastDelay) {
        return <div>Loading...</div>;
    } else {
        return null;
    }
}
