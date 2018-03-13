

import React from 'react';

import {shallow} from 'enzyme';

import {AggregateStats} from 'utils/stats';
import TagLocalesDashboardDataManager from 'tags/tag/dashboard/manager';
import TagLocaleStats from 'tags/tag/dashboard/stats';
import {TagLocalesStatsTable} from 'tags/tag/dashboard/table';
import {DashboardDataManager} from 'components/dashboard';
import {LocaleStatsTable} from 'widgets/tables';


test('TagLocalesDashboardDataManager constructor', () => {

    const manager = new TagLocalesDashboardDataManager(
        {props: {components: {foo: 113}},
         state: {
            data: {
                tag: {
                    data: [
                        {chart: {foo: 7, baz: 17},
                         name: 'X'},
                        {chart: {bar: 23, baz: 73},
                         name: 'Y'}]}}}});
    expect(manager instanceof DashboardDataManager).toBe(true);
    expect(manager.statsClass).toBe(TagLocaleStats);
    expect(manager.statData).toEqual(
        [{baz: 17, foo: 7, name: "X"},
         {bar: 23, baz: 73, name: "Y"}]);
    expect(manager.components.foo).toBe(113);
    const Body = manager.components.body;
    const body = shallow(<Body />);
    expect(body.text()).toBe("<DashboardBody />");
    expect(body.props()).toEqual(
        {components: {
            content: TagLocalesStatsTable}});
});


test('TagLocalesStatsTable render', () => {
    let table = shallow(<TagLocalesStatsTable />);
    expect(table.text()).toBe('');

    table = shallow(<TagLocalesStatsTable data={{tag: {data: 23}}} />);
    expect(table.text()).toBe("<LocaleStatsTable />");

    let stats = table.find(LocaleStatsTable);
    expect(stats.props()).toEqual(
        {columns: table.instance().columns,
         data: 23});
});


test('TagLocalesStats constructor', () => {
    const stats = new TagLocaleStats();
    expect(stats instanceof AggregateStats).toBe(true);
});


test('TagLocalesStats mostApproved', () => {
    let stats = new TagLocaleStats([]);
    expect(stats.mostApproved).toBe('');
    stats = new TagLocaleStats([
        {approved_strings: 7, name: 'foo'},
        {approved_strings: 23, name: 'bar'},
        {approved_strings: 13, name: 'baz'}]);
    expect(stats.mostApproved).toBe('bar');
});


test('TagLocalesStats mostMissingStrings', () => {
    let stats = new TagLocaleStats([]);
    expect(stats.mostMissingStrings).toBe('');
    stats = new TagLocaleStats([
        {approved_strings: 7, total_strings: 113, fuzzy_strings: 17, translated_strings: 43, name: 'foo'},
        {approved_strings: 23, total_strings: 113, fuzzy_strings: 17, translated_strings: 43, name: 'bar'},
        {approved_strings: 13, total_strings: 113, fuzzy_strings: 17, translated_strings: 43, name: 'baz'}])
    expect(stats.mostMissingStrings).toBe('foo');
});


test('TagLocalesStats mostSuggestions', () => {
    let stats = new TagLocaleStats([]);
    expect(stats.mostSuggestions).toBe('');
    stats = new TagLocaleStats([
        {translated_strings: 7, name: 'foo'},
        {translated_strings: 23, name: 'bar'},
        {translated_strings: 13, name: 'baz'}]);
    expect(stats.mostSuggestions).toBe('bar');
});


test('TagLocalesStats teamCount', () => {
    let stats = new TagLocaleStats([]);
    expect(stats.teamCount).toBe(0);
    stats = new TagLocaleStats([1, 2, 3]);
    expect(stats.teamCount).toBe(3);
});
