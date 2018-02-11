
import React from 'react';

import ReactTable from 'react-table';

import {shallow} from 'enzyme';

import {LatestActivity} from 'widgets/activity';
import {ProgressChart} from 'widgets/charts/progress';
import StatsTable from 'widgets/tables/stats/table';
import {TableHeader} from 'widgets/tables';
import {LocaleFilter, LocaleStatsTable} from 'widgets/tables/stats/locales';


test('StatsTable render', () => {
    const stats = shallow(<StatsTable />);

    // no data
    expect(stats.text()).toBe('');

    // add data, should be a table now
    stats.setProps({data: [7, 13, 23]});
    expect(stats.text()).toBe("<ReactTable />");

    // the table gets the expected props
    const table = stats.find(ReactTable);
    expect(table.props().data).toEqual([7, 13, 23]);
    expect(table.props().showPagination).toBe(false);
    expect(table.props().defaultPageSize).toBe(3);
    expect(table.props().className).toBe("stats-table");
    expect(table.props().columns).toEqual(stats.instance().columns);
    expect(table.props().SubComponent).toBe(undefined);
});


test('StatsTable render controls', () => {

    class MockStatsTable extends StatsTable {

        renderControls () {
            return 'CONTROLS';
        }
    }

    const stats = shallow(<MockStatsTable />);
    expect(stats.text()).toBe('CONTROLS');
});


test('StatsTable renderLatestActivity', () => {
    const stats = shallow(<StatsTable />);

    // if no activity data, renders empty string
    let activity = stats.instance().renderLatestActivity(
        {original: {activity: null}});
    expect(activity).toBe('');

    // render with activity data
    let props = {original: {activity: {FOO: 7, BAR: 23}}}
    activity = stats.instance().renderLatestActivity(props);
    expect(activity).toEqual(<LatestActivity {...props.original.activity} />);
});


test('StatsTable renderProgress', () => {
    const stats = shallow(<StatsTable />);

    // if no chart data, renders empty string
    let chart = stats.instance().renderProgress(
        {original: {chart: null}});
    expect(chart).toBe('');

    // render with chart data
    let props = {original: {chart: {FOO: 7, BAR: 23}}};
    let expected = {
        percentages: {"fuzzy": 0, "missing": 0, "suggested": 0, "total": 0, "translated": 0},
        stats: {"fuzzy": 0, "missing": 0, "suggested": 0, "All strings": 0, "translated": 0}};
    chart = stats.instance().renderProgress(props)
    expect(chart).toEqual(
        <div className="wrapper">
            <ProgressChart {...expected} />
        </div>);
});


test('StatsTable accessActivity', () => {
    const stats = shallow(<StatsTable />);
    expect(stats.instance().accessActivity({})).toBe(undefined);
    expect(stats.instance().accessActivity({activity: {date: 23}})).toBe(23);
});


test('StatsTable accessProgress', () => {
    const stats = shallow(<StatsTable />);
    expect(stats.instance().accessProgress({})).toBe(0);
    expect(stats.instance().accessProgress({chart: {approved_strings: 23}})).toBe(23);
});


test('StatsTable renderProgressHeader', () => {
    const stats = shallow(<StatsTable />);
    expect(stats.instance().renderProgressHeader()).toEqual(
        <TableHeader className="progress">Progress</TableHeader>);
});


test('StatsTable renderActivityHeader', () => {
    const stats = shallow(<StatsTable />);
    expect(stats.instance().renderActivityHeader()).toEqual(
        <TableHeader>Latest activity</TableHeader>);
});


test('StatsTable renderControls', () => {
    let stats = shallow(<StatsTable />);
    expect(stats.instance().renderControls()).toBe('');

    class MockControls extends React.PureComponent {

        render () {
            return 'CONTROLS: ' + this.props.foo + this.props.bar;
        }
    }
    stats = shallow(
        <StatsTable
           foo={7}
           bar={23}
           components={{controls: MockControls}} />);
    const controls = shallow(stats.instance().renderControls());
    expect(controls.text()).toBe('CONTROLS: 723');
});


test('LocaleStatsTable render', () => {
    const locales = shallow(<LocaleStatsTable data={23} />);
    expect(locales.text()).toBe("<StatsTable />");
    expect(locales.state().filter).toBe('');

    const stats = locales.find(StatsTable);

    expect(stats.props()).toEqual(
        {components: {
            controls: LocaleFilter},
         data: 23,
         className: '',
         columns: locales.instance().columns,
         handleFilterChange: locales.instance().handleFilterChange});
});


test('LocaleStatsTable columns', () => {
    let table = shallow(<LocaleStatsTable />);

    expect(table.instance().columns).toEqual(
        [table.instance().columnName,
         table.instance().columnCode,
         table.instance().columnSpeakers]);
    expect(table.instance().columnName).toEqual(
        {accessor: "name",
         resizable: false,
         width: 240,
         Cell: table.instance().renderName,
         Header: <TableHeader>Language</TableHeader>});
    expect(table.instance().columnCode).toEqual(
        {accessor: "code",
         resizable: false,
         width: 90,
         Cell: table.instance().renderCode,
         Header: <TableHeader>Locale</TableHeader>});
});


test('LocaleStatsTable renderCode', () => {
    let table = shallow(<LocaleStatsTable />);
    expect(table.instance().renderCode({original: {code: 'foo', url: 'bar'}})).toEqual(
        <span className="code"><a href="bar">foo</a></span>);
});


test('LocaleStatsTable renderName', () => {
    let table = shallow(<LocaleStatsTable />);
    expect(table.instance().renderName({original: {name: 'foo', url: 'bar'}})).toEqual(
        <h4><a href="bar">foo</a></h4>);
});


test('LocaleStatsTable data', () => {
    const data = [{name: 'foo'}, {name: 'bar'}, {name: 'baz'}];
    const locales = shallow(<LocaleStatsTable data={data} />);
    expect(locales.instance().data).toBe(data);

    locales.setState({filter: 'o'});
    expect(locales.instance().data).toEqual([{name: "foo"}]);

    locales.setState({filter: 'a'});
    expect(locales.instance().data).toEqual([{name: "bar"}, {name: "baz"}]);

    locales.setState({filter: 'z'});
    expect(locales.instance().data).toEqual([{name: "baz"}]);
});


test('LocaleStatsTable handleFilterChange', () => {
    const locales = shallow(<LocaleStatsTable />);
    expect(locales.state().filter).toBe('');

    locales.instance().handleFilterChange('foo');
    expect(locales.state().filter).toBe('foo');

    locales.instance().handleFilterChange('bar');
    expect(locales.state().filter).toBe('bar');
});


test('LocaleFilter render', () => {
    const filter = shallow(<LocaleFilter foo={7} bar={23} />);
    expect(filter.text()).toBe("<SearchControls />");
    expect(filter.props()).toEqual(
        {placeholder: "Filter teams",
         foo: 7,
         bar: 23});
});
