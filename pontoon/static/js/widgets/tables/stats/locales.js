
import React from 'react';

import Humanize from 'humanize-plus';

import StatsTable from './table';
import {TableHeader} from 'widgets/tables';
import {SearchControls} from 'widgets/search';


export class LocaleFilter extends React.PureComponent {

    render () {
        return (
            <SearchControls
               {...this.props}
               placeholder="Filter teams"
               />);
    }
}


export class LocaleStatsTable extends React.Component {

    constructor (props) {
        super(props);
        this.state = {filter: ''};
        this.handleFilterChange = this.handleFilterChange.bind(this);
    }

    handleFilterChange (text) {
        this.setState({filter: text});
    }

    get data () {
        const {filter} = this.state;
        if (filter) {
            return (this.props.data || []).filter(d => d.name.toLowerCase().includes(filter.toLowerCase()));
        }
        return this.props.data;
    }


    get columnCode () {
        return {
            Header: this.renderCodeHeader,
            resizable: false,
            accessor: 'code',
            width: 90,
            Cell: this.renderCode};
    }

    get columnName () {
        return {
            Header: this.renderNameHeader,
            resizable: false,
            accessor: 'name',
            width: 240,
            Cell: this.renderName};
    }

    get columnSpeakers () {
        return {
            Header: this.renderSpeakersHeader,
            resizable: false,
            accessor: 'speakers',
            width: 110,
            Cell: this.renderSpeakers};
    }

    get columns () {
        return [this.columnName, this.columnCode, this.columnSpeakers];
    }

    renderCode (item) {
        return (
            <span className="code"><a href="#">{item.original.code}</a></span>);
    }

    renderCodeHeader () {
        return (
            <TableHeader>
              Locale
            </TableHeader>);
    }

    renderName (item) {
        return (
            <h4><a href={item.original.url}>{item.original.name}</a></h4>);
    }

    renderNameHeader () {
        return (
            <TableHeader>
              Language
            </TableHeader>);
    }

    renderSpeakers (item) {
        return (
            <div className="wrapper">
              {Humanize.intComma(item.original.population)}
            </div>);
    }

    renderSpeakersHeader () {
        return (
            <TableHeader>
              Speakers
            </TableHeader>);
    }

    render () {
        const {data, ...props} = this.props;
        return (
            <StatsTable
               {...props}
               columns={this.columns}
               data={this.data}
               handleFilterChange={this.handleFilterChange}
               components={{controls: LocaleFilter}} />);
    }
}
