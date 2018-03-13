
import React from 'react';
import ReactTable from 'react-table';

import "react-table/react-table.css";
import './table.css';

import {ProgressChart} from 'widgets/charts';
import {LatestActivity} from 'widgets/activity';

import {Stats} from 'utils/stats';
import {TableHeader} from 'widgets/tables';


export default class StatsTable extends React.PureComponent {

    constructor (props) {
        super(props);
        this.renderProgress = this.renderProgress.bind(this);
    }

    get className () {
        return "stats-table";
    }

    get columnActivity () {
        return {
            id: "activity",
            accessor: this.accessActivity,
            Header: this.renderActivityHeader,
            resizable: false,
            width: 160,
            Cell: this.renderLatestActivity};
    }

    get columnProgress () {
        return {
            id: "progress",
            accessor: this.accessProgress,
            Header: this.renderProgressHeader,
            minWidth: 200,
            resizable: false,
            Cell: this.renderProgress};
    }

    get columns () {
        return (this.props.columns || []).concat([
            this.columnActivity,
            this.columnProgress]);
    }

    get components () {
        const components = {
            table: ReactTable};
        return Object.assign({}, components, (this.props.components || {}));
    }

    get defaultPageSize () {
        const {data} = this.props;
        return (data || []).length;
    }

    accessActivity (item) {
        return (item.activity ? item.activity.date : undefined);
    }

    accessProgress (item) {
        return (item.chart ? item.chart.approved_strings : 0);
    }

    progressData (data) {
        const stats = new Stats(data);
        return {
            stats: {
                translated: stats.translatedStrings,
                suggested: stats.suggestedStrings,
                fuzzy: stats.fuzzyStrings,
                missing: stats.missingStrings,
                'All strings': stats.totalStrings
            },
            percentages: {
                translated: stats.translatedShare,
                suggested: stats.suggestedShare,
                fuzzy: stats.fuzzyShare,
                missing: stats.missingShare,
                total: stats.approvedPercent}};
    }

    get showPagination () {
        return false;
    }

    get style () {
        return {width: '100%'};
    }

    render () {
        return (
            <div>
                {this.renderControls()}
                {this.renderTable()}
            </div>);
    }

    renderActivityHeader () {
        return <TableHeader>Latest activity</TableHeader>;
    }

    renderLatestActivity (item) {
        if (!item.original.activity) {
            return '';
        }
        return (
            <LatestActivity {...item.original.activity} />);
    }

    renderProgress (item) {
        if (!item.original.chart) {
            return '';
        }
        return (
            <div className="wrapper">
              <ProgressChart {...this.progressData(item.original.chart)} />
            </div>);
    }

    renderProgressHeader () {
        return <TableHeader className="progress">Progress</TableHeader>;
    }

    renderControls () {
        const {controls: Controls} = this.components;
        const {components, ...props} = this.props;
        if (!Controls) {
            return '';
        }
        return (
            <Controls
               {...props}
               />);
    }

    renderTable () {
        const {table: Table} = this.components;
        const {components, data, ...props} = this.props;
        if (!data) {
            return '';
        }
        return (
            <Table
               style={this.style}
               resizable={false}
               showPagination={this.showPagination}
               defaultPageSize={this.defaultPageSize}
               className={this.className}
               {...props}
               columns={this.columns}
               data={data}
               />);
    }
}
