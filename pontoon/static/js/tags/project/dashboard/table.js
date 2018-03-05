
import React from 'react';

import {StatsTable} from 'widgets/tables';
import {TableHeader} from 'widgets/tables';


export default class ProjectTagsStatsTable extends React.PureComponent {

    renderName (item) {
        return (
            <h4><a href={item.original.url}>{item.original.name}</a></h4>);
    }

    get columnName () {
        return {
            id: "tag",
            Header: this.renderTagHeader,
            resizable: false,
            accessor: 'tag',
            Cell: this.renderName};
    }

    renderPriority (item) {
        return (
            <div className="wrapper">{item.original.priority}</div>);
    }

    renderPriorityHeader () {
        return <TableHeader>Priority</TableHeader>;
    }

    renderTagHeader () {
        return <TableHeader>Tag</TableHeader>;
    }

    get columnPriority () {
        return {
            id: "priority",
            Header: this.renderPriorityHeader,
            resizable: false,
            accessor: 'priority',
            Cell: this.renderPriority};
    }

    get columns () {
        return [this.columnName, this.columnPriority];
    }

    render () {
        if (!this.props.data || !this.props.data.tags) {
            return '';
        }
        return (
            <StatsTable
               columns={this.columns}
               data={this.props.data.tags.data} />);
    }
}
