
import React from 'react';
import ReactTable from 'react-table';

import "react-table/react-table.css";
import './table.css';

import {getClass} from 'utils/classname';
import {ProgressChart} from 'widgets/charts/progress';
import {LatestActivity} from 'widgets/activity';

import {Stats} from 'utils/stats';
import {TableHeader} from 'widgets/tables';


export default class StatsTable extends React.PureComponent {
    className = "stats-table";
    components = {table: ReactTable};
    showPagination = false;
    style = {width: '100%'};

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

    renderProgress = (item) => {
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
        const {components, ...props} = this.props;
        const {controls: Controls} = (components || {});
        if (!Controls) {
            return '';
        }
        return (
            <Controls
               {...props}
               />);
    }

    renderTable () {
        const {components, data, ...props} = this.props;
        const {table: Table = this.components.table} = (components || {});
        if (!data) {
            return '';
        }
        return (
            <Table
               style={this.style}
               resizable={false}
               showPagination={this.showPagination}
               defaultPageSize={this.defaultPageSize}
               className={getClass(this)}
               {...props}
               columns={this.columns}
               data={data}
               />);
    }
}
