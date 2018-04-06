
import React from 'react';
import ReactTable from 'react-table';

import Humanize from 'humanize-plus';

import {appendProps} from 'utils/props';
import {getComponent} from 'utils/components';
import {TableHeader} from 'widgets/tables';
import {Columns} from 'widgets/columns';
import {AvatarLink} from 'widgets/images';
import {Buttons} from 'widgets/lists/buttons';

import "react-table/react-table.css";
import './contributors.css';
import './table.css';


export class ContributorsStatsTable extends React.Component {

    constructor (props) {
        super(props);
        this.state = {period: this.props.period || ''};
    }

    static get defaultProps () {
        return {
            buttons: {'All time': '', '12 months': '12', '6 months': '6', '3 months': '3', 'Last month': '1'},
            components: {table: ReactTable},
            resizable: false,
            showPagination: false,
            style: {width: '100%'}};
    }

    @appendProps
    get className () {"-striped stats-table"}

    get buttons () {
        const {period} = this.state;
        return Object.entries(this.props.buttons).map(
            ([b, k]) => ({value: b, name: k, active: period === k}));
    }

    get columnName () {
        return {
            Header: <TableHeader>Contributor</TableHeader>,
            resizable: false,
            accessor: 'name',
            width: 518,
            headerClassName: 'name',
            className: 'name',
            Cell: this.renderName};
    }

    get columnRank () {
        return {
            Header: <TableHeader>Rank</TableHeader>,
            resizable: false,
            accessor: 'userrank',
            width: 81,
            className: 'rank',
            headerClassName: 'rank',
            Cell: (item) => item.index + 1};
    }

    get columnTranslations () {
        return {
            Header: <TableHeader>Translations</TableHeader>,
            resizable: false,
            accessor: 'usertranslations',
            width: 380,
            className: 'translations',
            Cell: this.renderTranslations};
    }

    get columns () {
        return [this.columnRank, this.columnName, this.columnTranslations];
    }

    async componentDidUpdate(prevProps, prevState) {
        if (prevState !== this.state) {
            await this.props.refreshData(this.state);
        }
    }

    handleButtonClick = (evt) => {
        this.setState({period: evt.currentTarget.name});
    }

    renderControls () {
        return (
            <Buttons
               className="contributors"
               buttons={this.buttons}
               handleClick={this.handleButtonClick} />);
    }

    renderName (item) {
        const avatar = (
            <AvatarLink
               href={item.original.url}
               src={item.original.avatar}
               size={44}
               className="rounded">
              <p className="user-name">{item.original.name}</p>
            </AvatarLink>);
        return (
            [avatar, <p className="user-role">{item.original.role}</p>]);
    }

    renderTranslations = (item) => {
        const columns = Object.entries(item.original.stats).map(([k, v]) => {
            return [(
                <div className={'stat ' + k.toLowerCase()}>
                  <div className="title">{k}</div>
                  <div className="value">{Humanize.intComma(v)}</div>
                </div>),
                    2.5];
        });
        return <Columns columns={columns}/>;
    }

    render () {
        const {components, data, ...props} = this.props;
        const Table = getComponent(this, 'table');
        return [
            this.renderControls(),
            <Table
               defaultPageSize={this.defaultPageSize}
               columns={this.columns}
               {...props}
               className={this.className}
               data={data}
               />];
    }
}
