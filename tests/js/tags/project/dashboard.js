
import React from 'react';

import {shallow} from 'enzyme';

import ProjectTagsDashboardDataManager from 'tags/project/dashboard/manager';
import ProjectTagsStatsTable from 'tags/project/dashboard/table';
import {ProjectSummaryInfo} from 'projects/dashboard';
import {DashboardDataManager} from 'components/dashboard';
import {StatsTable} from 'widgets/tables';


test('ProjectTagsDashboardDataManager constructor', () => {
    const manager = new ProjectTagsDashboardDataManager(
        {props: {components: {foo: 113}},
         state: {
            data: {
                dashboard: {
                    context: {stats: 23}}}}});
    expect(manager instanceof DashboardDataManager).toBe(true);
    expect(manager.statData).toEqual(23);
    expect(manager.components.foo).toBe(113);

    const Header = manager.components.header;
    const header = shallow(<Header />);
    expect(header.text()).toBe("<DashboardHeader />");
    const Summary = header.props().components.summary;
    const summary = shallow(<Summary />);
    expect(summary.text()).toBe("<DashboardSummary />");
    expect(summary.props().components.info).toBe(ProjectSummaryInfo);

    const Body = manager.components.body;
    const body = shallow(<Body />);
    expect(body.text()).toBe("<DashboardBody />");
    expect(body.props()).toEqual(
        {components: {
            content: ProjectTagsStatsTable}});
});


test('ProjectTagsStatsTable render', () => {

    let table = shallow(<ProjectTagsStatsTable />);
    expect(table.text()).toBe('');

    table =  shallow(
        <ProjectTagsStatsTable
           data={{tags: {data: [23]}}}
           />);
    expect(table.text()).toBe("<StatsTable />");
    let stats = table.find(StatsTable);
    expect(stats.props()).toEqual(
        {columns: table.instance().columns,
         data: [23]});
});


test('ProjectTagsStatsTable columns', () => {
    let table = shallow(<ProjectTagsStatsTable />);
    expect(table.instance().columns).toEqual([
        table.instance().columnName, table.instance().columnPriority]);
    expect(table.instance().columnName).toEqual(
        {Cell: table.instance().renderName,
         id: "tag",
         accessor: "tag",
         resizable: false,
         Header: table.instance().renderTagHeader});
});


test('ProjectTagsStatsTable renderName', () => {
    let table = shallow(<ProjectTagsStatsTable />);
    let name = shallow(
        table.instance().renderName(
            {original: {url: 7, name: 23}}));
    expect(name.text()).toBe("23");
    expect(name.find('h4').find('a').props()).toEqual(
        {children: 23,
         href: 7});
});
