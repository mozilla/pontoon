

import React from 'react';

import {shallow} from 'enzyme';

import Humanize from 'humanize-plus';

import {Columns} from 'widgets/columns';
import {InfoList} from 'widgets/lists/info';
import {
    Dashboard, DashboardBody, DashboardDataManager,
    DashboardHeader, DashboardNavigation} from 'components/dashboard';
import DashboardSummary from 'components/dashboard/header/summary';
import SummaryChart from 'components/dashboard/header/summary/chart';
import {SummaryStats, StatItem} from 'components/dashboard/header/summary/stats';
import Toolbar from 'components/toolbar';
import {Section} from 'widgets/section';
import {TabList} from 'widgets/lists/tabs';
import {List, ListItem} from 'widgets/lists/generic';
import {Title} from 'widgets/title';
import {WheelChart} from 'widgets/charts';
import {DataManager} from 'utils/data';
import {Stats} from 'utils/stats';


test('Dashboard render', () => {
    const refreshData = jest.fn(async () => undefined);
    const manager = {
        components: {},
        content: 7,
        summaryInfo: 73,
        summaryStats: 113,
        toolbar: 13,
        tabs: 43};
    let dashboard = shallow(
        <Dashboard
           refreshData={refreshData}
           manager={manager} />);
    expect(dashboard.text()).toBe('');

    dashboard = shallow(
        <Dashboard
           refreshData={refreshData}
           data={{foo: 23, bar: 17}}
           manager={manager} />);
    expect(dashboard.text()).toBe(
        "<Toolbar /><DashboardHeader /><DashboardNavigation /><DashboardBody />");

    const toolbar = dashboard.find(Toolbar);
    expect(toolbar.props().components).toEqual(
        dashboard.instance().components);
    expect(toolbar.props().toolbar).toBe(13);

    const header = dashboard.find(DashboardHeader);
    expect(header.props().components).toEqual(
        dashboard.instance().components);
    expect(header.props().stats).toBe(113);

    const navigation = dashboard.find(DashboardNavigation);
    expect(navigation.props().components).toEqual(
        dashboard.instance().components);
    expect(navigation.props().tabs).toBe(43);

    const body = dashboard.find(DashboardBody);
    expect(body.props().components).toEqual(
        dashboard.instance().components);
    expect(body.props().content).toBe(7);
});


test('DashboardBody render', () => {
    let body = shallow(<DashboardBody />);
    expect(body.text()).toBe('');

    class MockContent extends React.PureComponent {

        render () {
            return "CONTENT";
        }
    }

    body = shallow(
        <DashboardBody
           foo={7}
           bar={23}
           components={{content: MockContent}} />);
    expect(body.text()).toBe('<Section />');
    let section = body.find(Section);
    expect(section.props()).toEqual(
        {children: <MockContent foo={7} bar={23} />,
         "id": "main"});
});


test('DashboardNavigation render', () => {
    let navigation = shallow(<DashboardNavigation />);
    expect(navigation.text()).toBe('<Section />');

    let section = navigation.find(Section);
    expect(section.props()).toEqual({"children": <TabList />, "id": "middle"});

    class MockNavigation extends React.PureComponent {

        render () {
            return "NAVIGATION";
        }
    }

    navigation = shallow(
        <DashboardNavigation
           foo={7}
           bar={23}
           components={{navigation: MockNavigation}} />);
    expect(navigation.text()).toBe('<Section />');
    section = navigation.find(Section);
    expect(section.props()).toEqual(
        {children: <TabList bar={23} components={{navigation: MockNavigation}} foo={7} />,
         id: 'middle'});

});


test('DashboardHeader render', () => {

    class MockDashboardHeader extends DashboardHeader {

        renderTitle () {
            return 'TITLE';
        }

        renderSummary () {
            return 'SUMMARY';
        }
    }

    let header = shallow(<MockDashboardHeader />);
    expect(header.text()).toBe('<Section />');

    let section = header.find(Section);
    expect(section.props()).toEqual(
        {children: ["TITLE", "SUMMARY"],
         id: "heading"});
});


test('DashboardHeader renderSummary', () => {

    let header = shallow(<DashboardHeader />);
    let summary = header.instance().renderSummary();
    expect(summary).toEqual(<DashboardSummary />);

    class MockSummary extends DashboardSummary {

    }

    header = shallow(
        <DashboardHeader
           foo={7}
           bar={23}
           components={{baz: 73, summary: MockSummary}}
           />);
    summary = header.instance().renderSummary();
    expect(summary).toEqual(<MockSummary bar={23} foo={7} />);
});


test('DashboardHeader renderTitle', () => {

    let header = shallow(<DashboardHeader />);
    let title = header.instance().renderTitle();
    expect(title).toEqual(<Title />);

    class MockTitle extends Title {

    }

    header = shallow(
        <DashboardHeader
           foo={7}
           bar={23}
           components={{baz: 73, title: MockTitle}}
           />);
    title = header.instance().renderTitle();
    expect(title).toEqual(<MockTitle bar={23} foo={7} />);
});


test('DashboardSummary render', () => {

    let summary = shallow(<DashboardSummary />);
    expect(summary.text()).toBe("<Columns />");
    let columns = summary.find(Columns);
    expect(columns.props()).toEqual(
        {columns: [
            [<InfoList items={undefined} />, 3],
            [<SummaryChart />, 2],
            [<SummaryStats />, 3]]});


    class MockInfoList extends InfoList {
    }

    class MockSummaryChart extends SummaryChart {
    }

    class MockSummaryStats extends SummaryStats {
    }

    summary = shallow(
        <DashboardSummary
           components={{info: MockInfoList, chart: MockSummaryChart, stats: MockSummaryStats}}
           foo={7}
           bar={23}
           info={73}
           />);
    expect(summary.text()).toBe("<Columns />");
    columns = summary.find(Columns);
    expect(columns.props()).toEqual(
        {columns: [
            [<MockInfoList info={73} foo={7} bar={23} />, 3],
            [<MockSummaryChart info={73} foo={7} bar={23} />, 2],
            [<MockSummaryStats info={73} foo={7} bar={23} />, 3]]});
});


test('SummaryChart render', () => {
    let chart = shallow(<SummaryChart />);
    expect(chart.text()).toBe('');
    const stats = {
        fuzzy: {value: 7},
        translated: {value: 13},
        suggested: {value: 17},
        missing: {value: 23},
        all: {value: 43}};
    chart = shallow(
        <SummaryChart
           stats={stats} />);
    expect(chart.text()).toBe("<WheelChart />");
    let wheel = chart.find(WheelChart);
    expect(wheel.props()).toEqual(
        {data: {fuzzy: {color: "rgb(254, 210, 113)", value: 7},
                missing: {color: "rgb(77, 89, 103)", value: 23},
                suggested: {color: "rgb(79, 196, 246)", value: 17},
                translated: {color: "rgb(123, 200, 118)", value: 13}},
         percentage: 30,
         total: 43});
});


test('SummaryStats render', () => {
    let stats = shallow(<SummaryStats />);
    expect(stats.text()).toBe('');

    stats = shallow(<SummaryStats stats={{foo: 7, bar: 23}} />);
    expect(stats.text()).toBe("<List />");
    let list = stats.find(List);
    expect(list.props()).toEqual({
        className: "legend",
        components: {
            item: StatItem},
        items: [["foo", 7], ["bar", 23]]});
});


test('StatItem render', () => {
    Humanize.intComma = jest.fn(() => 73);

    const item = ['foo', {value: 7, label: 23}];
    let stats = shallow(<StatItem {...item} />);
    expect(stats.text()).toBe("<ListItem />");

    let listitem = stats.find(ListItem);
    const {children, ...props} = listitem.props();

    expect(props).toEqual({className: "foo"});
    expect(children.length).toBe(3);
    expect(children[0]).toEqual(<span className="fa status" />);
    expect(children[1]).toBe(23);
    expect(shallow(children[2]).props()).toEqual(
        {children: 73, className: "value", "data-value": 7});
    expect(Humanize.intComma.mock.calls).toEqual([[7]]);
});


test('DashboardDataManager constructor', () => {
    const component = {foo: 7, bar: 23, props: {}};
    const manager = new DashboardDataManager(component);
    expect(manager instanceof DataManager).toBe(true);
    expect(manager.component).toBe(component);
    expect(manager.statData).toEqual({});
    expect(manager.statsClass).toBe(Stats);
    expect(manager.components).toEqual({});
})


test('DashboardDataManager components', () => {
    const component = {props: {components: 23}};
    const manager = new DashboardDataManager(component);
    expect(manager.components).toBe(23);
});


test('DashboardDataManager dashboard', () => {
    const component = {
        state: {
            data: {
                dashboard: {
                    tabs: 7,
                    toolbar: 23,
                    context: {
                        title: 43}}}}};
    const manager = new DashboardDataManager(component);
    expect(manager.tabs).toBe(7);
    expect(manager.toolbar).toBe(23);
    expect(manager.title).toBe(43);
});


test('DashboardDataManager stats', () => {

    class MockStats {

        constructor (data) {
            this.data = data;
        }
    }

    class MockDashboardDataManager extends DashboardDataManager {

        get statData () {
            return 23;
        }

        get statsClass () {
            return MockStats;
        }
    }

    const manager = new MockDashboardDataManager();
    const stats = manager.stats
    expect(stats instanceof MockStats).toBe(true);
    expect(stats.data).toBe(23)
});


test('DashboardDataManager summaryInfo', () => {

    class MockDashboardDataManager extends DashboardDataManager {

        get stats () {
            return {
                teamCount: 7,
                mostTranslations: 11,
                mostSuggestions: 13,
                mostMissingStrings: 17,
                mostApproved: 19}
        }
    }

    const manager = new MockDashboardDataManager();
    expect(manager.summaryInfo).toEqual(
        {"Most enabled strings": 19,
         "Most missing strings": 17,
         "Most suggestions": 13,
         "Most translations": 11,
         "Number of teams": 7})
});


test('DashboardDataManager summaryStats', () => {

    class MockDashboardDataManager extends DashboardDataManager {

        get stats () {
            return {
                translatedStrings: 7,
                suggestedStrings: 11,
                fuzzyStrings: 13,
                missingStrings: 17,
                totalStrings: 19}
        }
    }

    const manager = new MockDashboardDataManager();
    expect(manager.summaryStats).toEqual(
        {"all": {"label": "All strings", "value": 19},
         "fuzzy": {"label": "Fuzzy strings", "value": 13},
         "missing": {"label": "Missing strings", "value": 17},
         "suggested": {"label": "Suggested strings", "value": 11},
         "translated": {"label": "Translated strings", "value": 7}});
});
