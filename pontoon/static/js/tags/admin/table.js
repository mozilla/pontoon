
import React from 'react';
import ReactTable from 'react-table';
import "react-table/react-table.css";

import Checkbox from 'widgets/checkbox';


export default class TagResourceTable extends React.Component {

    constructor (props) {
        super(props);
        this.visible = [];
        this.state = {checked: new Set()};

        this.handleCheckboxClick = this.handleCheckboxClick.bind(this);
        this.handleSelectAll = this.handleSelectAll.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleTableChange = this.handleTableChange.bind(this);
        this.handleTableSortChange = this.handleTableSortChange.bind(this);
        this.handleTableResize = this.handleTableResize.bind(this);

        this.renderResource = this.renderResource.bind(this);
        this.renderResourceCheckbox = this.renderResourceCheckbox.bind(this);
        this.renderSelectAllCheckbox = this.renderSelectAllCheckbox.bind(this);
    }

    get columns () {
        // column descriptors, as expected by ReactTable
        return [
            {Header: this.renderSelectAllCheckbox,
             Cell: this.renderResourceCheckbox,
             sortable: false,
             width: 45
            },
            {Header: "Resource",
             id: "type",
             Cell: this.renderResource
            }];
    }

    get defaultPageSize () {
        return 5;
    }

    get pruned() {
        // Returns a copy of the checked set with any resource paths that are
        // not in `this.visible` removed
        let {checked} = this.state;
        return new Set([...checked].filter(v => (this.visible.indexOf(v) !== -1)))
    }

    get selected () {
        // get the pruned list of selected resources, returns all=true/false
        // if all visible resources are selected
        // some rows can be empty strings if there are more visible rows than
        // resources
        const checked = this.pruned
        const all = (
            checked.size > 0
                && checked.size === this.visible.filter(v => v !== '').length);
        return {all, checked};
    }

    get submitMessage () {
        const {type} = this.props;
        return type === 'assoc' ? 'Unlink resources': 'Link resources';
    }

    componentWillUpdate (prevProps) {
        if (prevProps.data !== this.props.data) {
            this.visible.length = 0;
            this.setState({checked: new Set()});
        }
    }

    handleCheckboxClick (evt) {
        // adds/removes paths for submission
        let {checked} = this.state;
        checked = new Set(checked);
        evt.target.checked ? checked.add(evt.target.name) : checked.delete(evt.target.name);
        this.setState({checked});
    }

    handleSelectAll () {
        // user clicked the select all checkbox...
        // if there are some resources checked already, all are removed
        // otherwise all visible are checked.
        let {checked} = this.state;
        checked = checked.size > 0 ? new Set() : new Set([...this.visible])
        return this.setState({checked})
    }

    async handleSubmit (evt) {
        // after emitting handleSubmit to parent with list of currently
        // checked, clears the checkboxes
        evt.preventDefault();
        const {checked} = this.state;
        await this.props.handleSubmit([...checked]);
        await this.setState({checked: new Set()});
    }

    handleTableChange () {
        this.visible.length = 0;
        return this.setState({checked: new Set()});
    }

    handleTableResize (pageSize) {
        this.visible.length = pageSize;
        return this.setState({checked: this.pruned});
    }

    handleTableSortChange () {
        return this.setState({checked: this.pruned});
    }

    render () {
        return (
            <div>
              {this.renderTable()}
              {this.renderSubmit()}
            </div>);
    }

    renderResource (item) {
        this.visible.length = item.pageSize;
        this.visible[item.viewIndex] = item.original[0];
        return <span>{item.original[0]}</span>;
    }

    renderResourceCheckbox (data) {
        const {checked} = this.state;
        return (
            <Checkbox
               checked={checked.has(data.original[0])}
               name={data.original[0]}
               onChange={this.handleCheckboxClick} />);
    }

    renderSelectAllCheckbox () {
        // renders a select all checkbox, sets the check to
        // indeterminate if only some of the visible resources
        // are checked
        let {all, checked} = this.selected;
        return (
            <Checkbox
               checked={all}
               indeterminate={!all && checked.size > 0}
               onClick={this.handleSelectAll} />);
    }

    renderSubmit () {
        return (
            <button
               className="tag-resources-associate"
               onClick={this.handleSubmit}>
              {this.submitMessage}
            </button>);
    }

    renderTable () {
        return (
            <ReactTable
               defaultPageSize={this.defaultPageSize}
               className="-striped -highlight"
               data={this.props.data}
               onPageChange={this.handleTableChange}
               onPageSizeChange={this.handleTableResize}
               onSortedChange={this.handleTableSortChange}
               columns={this.columns} />);
    }
}
