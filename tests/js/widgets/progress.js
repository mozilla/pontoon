
import React from 'react';

import {shallow} from 'enzyme';

import Humanize from 'humanize-plus';

import {List, ListItem} from 'widgets/lists/generic';

import {
    ProgressChart, ProgressChartData, ProgressChartDataItem,
    ProgressChartLegend, ProgressChartLegendItem} from 'widgets/charts/progress';


test('ProgressChart render', () => {
    const data = {stats: 7, percentages: 23};
    const progress = shallow(<ProgressChart {...data} />);
    expect(progress.text()).toBe(
        "<ProgressChartData /><ProgressChartLegend />");
    let chart = progress.find(ProgressChartData);
    expect(chart.props()).toEqual({data: 23});

    let legend = progress.find(ProgressChartLegend);
    expect(legend.props()).toEqual({items: 7});
});


test('ProgressChartData render', () => {

    class MockProgressChartData extends ProgressChartData {

        renderTotal () {
            return 7;
        }

        renderChart () {
            return 23;
        }
    }
    const chart = shallow(<MockProgressChartData />);
    expect(chart.text()).toBe('723');
});


test('ProgressChartData renderTotal', () => {
    const stats = {total: 23};
    const chart = shallow(<ProgressChartData data={stats} />);
    expect(shallow(chart.instance().renderTotal()).text()).toEqual('23%');
});


test('ProgressChartData components', () => {
    const stats = {translated: 23, fuzzy: 13, suggested: 23, missing: 73, total: 43};
    const chart = shallow(<ProgressChartData data={stats} />);
    expect(chart.text()).toBe("43%<ProgressChartDataItem /><ProgressChartDataItem /><ProgressChartDataItem /><ProgressChartDataItem />");
    const items = chart.find(ProgressChartDataItem);
    items.forEach((item, i) => {
        const [k, v] = Object.entries(stats)[i];
        expect(item.props()).toEqual({className: k, data: v});
    });
});


test('ProgressChartLegend render', () => {
    let chart = shallow(<ProgressChartLegend items={[1, 2, 3]} />);
    expect(chart.text()).toBe('<List />');
    let list = chart.find(List);
    expect(list.props()).toEqual(
        {className: "legend",
         components: {item: ProgressChartLegendItem},
         items: [["0", 1], ["1", 2], ["2", 3]]});

    chart = shallow(
        <ProgressChartLegend
           components={{foo: 23, item: 7}}
           items={[1, 2, 3]} />);
    list = chart.find(List);
    expect(list.props()).toEqual(
        {className: "legend",
         components: {item: 7},
         items: [["0", 1], ["1", 2], ["2", 3]]});
});


test('ProgressChartDataItem render', () => {
    let item = shallow(<ProgressChartDataItem />);
    expect(item.text()).toBe('');
    let span = item.find('span');
    expect(span.length).toBe(1);
    expect(span.props()).toEqual({className: undefined, style: {width: "undefined%"}});

    item = shallow(<ProgressChartDataItem data={23} className="foo" />);
    expect(item.text()).toBe('');
    span = item.find('span');
    expect(span.length).toBe(1);
    expect(span.props()).toEqual({className: "foo", style: {width: "23%"}});

});


test('ProgressChartLegendItem render', () => {
    let item = shallow(<ProgressChartLegendItem />);
    expect(item.text()).toBe('<ListItem />');
    let span = item.find(ListItem);
    expect(span.props()).toEqual(
        {children: <a href="?status=undefined"><div className="title" /><div className="value" data-value={undefined}>0</div></a>});

    Humanize.intComma = jest.fn((v) => 2 * v);

    const props = [7, 23];
    item = shallow(<ProgressChartLegendItem {...props} />);
    expect(item.text()).toBe('<ListItem />');
    span = item.find(ListItem);

    const content = shallow(span.props().children);
    expect(content.text()).toBe('746');
    expect(content.props().href).toBe("?status=7");
    const title = content.find('div.title');
    expect(title.text()).toBe('7');

    const value = content.find('div.value');
    expect(value.props()['data-value']).toBe(23);
    expect(value.text()).toBe('46');
});
