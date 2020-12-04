import React from 'react';
import ReactTable from 'react-table';
import 'react-table/react-table.css';

import Checkbox from 'widgets/checkbox';

export default class CheckboxTable extends React.Component {
    constructor(props) {
        super(props);
        this.visible = [];
        this.state = { checked: new Set() };
    }

    get columns() {
        return [this.columnSelect].concat(this.props.columns || []);
    }

    get columnSelect() {
        return {
            Header: this.renderSelectAllCheckbox,
            Cell: this.renderCheckbox,
            sortable: false,
            width: 45,
        };
    }

    get defaultPageSize() {
        return this.props.defaultPageSize || 5;
    }

    get selected() {
        // get the pruned list of selected resources, returns all=true/false
        // if all visible resources are selected
        // some rows can be empty strings if there are more visible rows than
        // resources
        const checked = this.prune(this.state);
        const all =
            checked.size > 0 &&
            checked.size === this.visible.filter((v) => v !== '').length;
        return { all, checked };
    }

    clearTable() {
        this.visible.length = 0;
        this.setState({ checked: new Set() });
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        if (nextProps.data !== this.props.data) {
            this.clearTable();
        }
    }

    handleCheckboxClick = (evt) => {
        // adds/removes paths for submission
        const { name, checked: targetChecked } = evt.target;
        this.setState((prevState) => {
            let { checked } = prevState;
            checked = new Set(checked);
            targetChecked ? checked.add(name) : checked.delete(name);
            return { checked };
        });
    };

    handleSelectAll = () => {
        // user clicked the select all checkbox...
        // if there are some resources checked already, all are removed
        // otherwise all visible are checked.
        this.setState((prevState) => {
            let { checked } = prevState;
            checked =
                checked.size > 0
                    ? new Set()
                    : new Set([...this.visible.filter((x) => x)]);
            return { checked };
        });
    };

    handleSubmit = async (evt) => {
        // after emitting handleSubmit to parent with list of currently
        // checked, clears the checkboxes
        evt.preventDefault();
        const { checked } = this.state;
        await this.props.handleSubmit({ data: [...checked] });
        this.setState({ checked: new Set() });
    };

    handleTableChange = () => {
        this.clearTable();
    };

    handleTableResize = (pageSize) => {
        this.visible.length = pageSize;
        this.setState((prevState) => ({ checked: this.prune(prevState) }));
    };

    handleTableSortChange = () => {
        this.setState((prevState) => ({ checked: this.prune(prevState) }));
    };

    prune(state) {
        // Returns a copy of the checked set with any resource paths that are
        // not in `this.visible` removed
        let { checked } = state;
        return new Set(
            [...checked].filter((v) => this.visible.indexOf(v) !== -1)
        );
    }

    render() {
        return (
            <div>
                {this.renderTable()}
                {this.renderSubmit()}
            </div>
        );
    }

    renderCheckbox = (item) => {
        const { checked } = this.state;
        this.visible.length = item.pageSize;
        this.visible[item.viewIndex] = item.original[0];
        return (
            <Checkbox
                checked={checked.has(item.original[0])}
                name={item.original[0]}
                onChange={this.handleCheckboxClick}
            />
        );
    };

    renderSelectAllCheckbox = () => {
        // renders a select all checkbox, sets the check to
        // indeterminate if only some of the visible resources
        // are checked
        let { all, checked } = this.selected;
        return (
            <Checkbox
                checked={all}
                indeterminate={!all && checked.size > 0}
                onClick={this.handleSelectAll}
            />
        );
    };

    renderSubmit() {
        return (
            <button
                className={this.props.submitClass}
                onClick={this.handleSubmit}
            >
                {this.props.submitMessage}
            </button>
        );
    }

    renderTable() {
        return (
            <ReactTable
                defaultPageSize={this.defaultPageSize}
                className='-striped -highlight'
                data={this.props.data}
                onPageChange={this.handleTableChange}
                onPageSizeChange={this.handleTableResize}
                onSortedChange={this.handleTableSortChange}
                columns={this.columns}
            />
        );
    }
}
