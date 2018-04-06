
import React from 'react';

import Humanize from 'humanize-plus';

import {appendProps} from 'utils/props';
import {getClass} from 'utils/classname';
import {TableHeader} from 'widgets/tables';
import {SearchControls} from 'widgets/search';

import StatsTable from './table';


export class LocaleFilter extends React.PureComponent {

    render () {
        return (
            <SearchControls
               placeholder="Filter teams"
               {...this.props}
               />);
    }
}


export class LocaleStatsTable extends React.Component {
    components = {controls: LocaleFilter};
    state = {filter: ''};

    @appendProps
    get className () {"-highlighted locales-table"}

    get data () {
        const {filter} = this.state;
        if (filter) {
            return (this.props.data || []).filter(d => d.name.toLowerCase().includes(filter.toLowerCase()));
        }
        return this.props.data;
    }


    get columnCode () {
        return {
            Header: <TableHeader>Locale</TableHeader>,
            resizable: false,
            accessor: 'code',
            width: 90,
            Cell: this.renderCode};
    }

    get columnName () {
        return {
            Header: <TableHeader>Language</TableHeader>,
            resizable: false,
            accessor: 'name',
            width: 240,
            Cell: this.renderName};
    }

    get columnSpeakers () {
        return {
            Header: <TableHeader>Speakers</TableHeader>,
            resizable: false,
            accessor: 'speakers',
            width: 110,
            Cell: this.renderSpeakers};
    }

    get columns () {
        return [this.columnName, this.columnCode, this.columnSpeakers];
    }

    handleFilterChange = (text) => {
        this.setState({filter: text});
    }

    renderCode (item) {
        return (
            <span className="code">
              <a href={item.original.url}>
                {item.original.code}
              </a>
            </span>);
    }

    renderName (item) {
        return (
            <h4><a href={item.original.url}>{item.original.name}</a></h4>);
    }

    renderSpeakers (item) {
        return (
            <div className="wrapper">
              {Humanize.intComma(item.original.population)}
            </div>);
    }

    render () {
        const {data, ...props} = this.props;
        return (
            <StatsTable
               components={this.components}
               className={getClass(this)}
               {...props}
               columns={this.columns}
               data={this.data}
               handleFilterChange={this.handleFilterChange} />);
    }
}
