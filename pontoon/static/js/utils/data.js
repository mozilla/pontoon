import React from 'react';

import { ajax } from 'utils/ajax';

export class DataManager {
    constructor(state) {
        this.state = state;
    }

    get data() {
        return this.state.data;
    }

    get errors() {
        return this.state.errors;
    }
}

export function dataManager(WrappedComponent, Manager, data) {
    return class Wrapper extends React.Component {
        constructor(props) {
            super(props);
            this.state = { errors: {}, data: data };
        }

        get api() {
            return this.props.api;
        }

        get requestMethod() {
            return this.props.requestMethod || 'get';
        }

        get submitMethod() {
            return this.props.submitMethod || this.requestMethod;
        }

        refreshData = async (params) => {
            return this.handleResponse(
                await ajax.fetch(this.api, params, {
                    method: this.requestMethod,
                }),
            );
        };

        handleResponse = async (response) => {
            const { status } = response;
            const json = await response.json();
            if (status === 200) {
                const { data } = json;
                this.setState({ data, errors: {} });
                return;
            }
            const { errors } = json;
            this.setState({ errors });
        };

        handleSubmit = async (params) => {
            return this.handleResponse(
                await ajax.fetch(this.api, params, {
                    method: this.submitMethod,
                }),
            );
        };

        render() {
            Manager = Manager || DataManager;
            const manager = new Manager(this.state);
            return (
                <WrappedComponent
                    manager={manager}
                    errors={manager.errors}
                    data={manager.data}
                    handleSubmit={this.handleSubmit}
                    refreshData={this.refreshData}
                    {...this.props}
                />
            );
        }
    };
}
