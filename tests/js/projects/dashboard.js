
import React from 'react';

import {shallow} from 'enzyme';

import {ProjectSummaryInfo} from 'projects/dashboard';
import {InfoList} from 'widgets/lists/info';


test('ProjectSummaryInfo constructor', () => {

    class MockProjectSummaryInfo extends ProjectSummaryInfo {

        get summaryInfo () {
            return {
                foo: 7,
                bar: 23};
        }
    }

    let info = shallow(<MockProjectSummaryInfo />);
    expect(info.text()).toBe('');

    info = shallow(
        <MockProjectSummaryInfo
           data={{dashboard: {context: 13}}}
           baz0={43}
           baz1={73} />);
    expect(info.text()).toBe("<InfoList />");

    const list = info.find(InfoList);
    expect(list.props()).toEqual(
        {baz0: 43, baz1: 73, items: {bar: 23, foo: 7}});
});


test('ProjectSummaryInfo summaryInfo', () => {
    let info = shallow(<ProjectSummaryInfo />);
    info.instance().renderPriority = jest.fn(() => 'PRIORITY');
    info.instance().renderDeadline = jest.fn(() => 'DEADLINE');
    info.instance().renderRepository = jest.fn(() => 'REPOSITORY');
    info.instance().renderUser = jest.fn(() => 'USER');
    expect(info.instance().summaryInfo).toEqual(
        {"Contact Person": "USER",
         "Deadline": "DEADLINE",
         "Priority": "PRIORITY",
         "Repository": "REPOSITORY"});
});


test('ProjectSummaryInfo renderDeadline', () => {


    class MockProjectSummaryInfo extends ProjectSummaryInfo {

        renderPriority () {
            return 'PRIORITY';
        }

        renderRepository () {
            return 'REPOSITORY';
        }

        renderUser () {
            return 'USER';
        }
    }

    let info = shallow(
        <MockProjectSummaryInfo
           data={{dashboard: {context: {deadline: 23}}}} />);
    let deadline = shallow(info.instance().renderDeadline());
    expect(deadline.props()).toEqual(
        {children: "January 1, 1970",
         className: "overdue",
         dateTime: 23});
});


test('ProjectSummaryInfo renderPriority', () => {

    class MockProjectSummaryInfo extends ProjectSummaryInfo {

        renderDeadline () {
            return 'DEADLINE';
        }

        renderRepository () {
            return 'REPOSITORY';
        }

        renderUser () {
            return 'USER';
        }
    }

    let info = shallow(
        <MockProjectSummaryInfo
           data={{dashboard: {context: {priority: 3}}}} />);

    let priority = shallow(info.instance().renderPriority());
    const {children, ...props} = priority.props();
    expect(props).toEqual({"className": "stars"});
    expect(children.length).toBe(5);
    children.forEach((child, i) => {
        expect(shallow(child).text()).toBe("<Icon />");
        let props = {
            className: "star active",
            name: "star"}
        if (i > 2) {
            props.className = "star";
        }
        expect(shallow(child).props()).toEqual(props);
    });
});


test('ProjectSummaryInfo renderUser', () => {

    class MockProjectSummaryInfo extends ProjectSummaryInfo {

        renderDeadline () {
            return 'DEADLINE';
        }

        renderRepository () {
            return 'REPOSITORY';
        }

        renderPriority () {
            return 'PRIORITY';
        }
    }

    let info = shallow(
        <MockProjectSummaryInfo
           data={{dashboard: {context: {user: {url: 7, name: 23}}}}} />);

    let user = shallow(info.instance().renderUser());
    expect(shallow(user.props().children).props()).toEqual(
        {children: 23,
         href: 7});
});
