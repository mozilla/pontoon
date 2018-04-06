

import React from 'react';

import {mount, shallow} from 'enzyme';

import WheelChart from 'widgets/charts/wheel';


test('WheelChart render', () => {
    const drawChart = jest.fn();
    const drawing = {lineWidth: 17};
    const canvas = {getContext: jest.fn(() => drawing), width: 23, height: 113};

    class MockWheelChart extends WheelChart {

        drawChart () {
            drawChart.apply(this, arguments);
        }

        get canvas () {
            return canvas;
        }

        renderCanvas () {
            return 'CANVAS';
        }

        renderPercentage () {
            return 'PERCENTAGE';
        }
    }

    let chart = shallow(<MockWheelChart />);
    expect(chart.text()).toBe('CANVASPERCENTAGE');
    expect(drawChart.mock.calls).toEqual([[]]);
    expect(chart.find('div.wheel-chart').length).toBe(1)
    expect(chart.instance().canvasClassName).toBe('drawing');
    expect(chart.instance().className).toBe('wheel-chart');
    expect(chart.instance().height).toBe('130px');
    expect(chart.instance().width).toBe('130px');
    expect(chart.instance().percentageClassName).toBe(
        'number react-number noselect');
    expect(chart.instance().radius).toBe((canvas.width - drawing.lineWidth) / 2);

    drawChart.mockClear();
    chart.instance().componentDidUpdate();
    expect(drawChart.mock.calls).toEqual([[]]);
});


test('WheelChart renderPercentage', () => {

    class MockWheelChart extends WheelChart {

        drawChart () {
            return;
        }
    }

    let chart = shallow(
        <MockWheelChart
           percentage={23}
           percentageClassName="foo"
           />);
    let percentage = chart.find('span.foo');
    expect(percentage.length).toBe(1);
    expect(percentage.props().children).toBe(23);
});


test('WheelChart renderCanvas', () => {

    class MockWheelChart extends WheelChart {

        drawChart () {
            return;
        }
    }

    let chart = mount(
        <MockWheelChart
           height={73}
           width={113}
           canvasClassName="bar"
           />);
    let canvas = chart.find('canvas.bar');
    expect(canvas.length).toBe(1);
    expect(canvas.props().height).toBe(73);
    expect(canvas.props().width).toBe(113);
    expect(chart.instance().canvas).toBe(canvas.instance());
});


test('WheelChart props', () => {
    const drawChart = jest.fn();
    const drawing = {lineWidth: 17};
    const canvas = {getContext: jest.fn(() => drawing), width: 23, height: 113};

    class MockWheelChart extends WheelChart {

        drawChart () {
            drawChart.apply(this, arguments);
        }

        get canvas () {
            return canvas;
        }
    }

    let chart = shallow(
        <MockWheelChart
           canvasClassName="foo"
           className="FOO"
           height="bar"
           width="baz"
           />);
    const wrapper = chart.find('div.FOO');
    expect(wrapper.props().children[0].props).toEqual({"className": "foo", "height": "bar", "width": "baz"});
    expect(wrapper.props().children[1].props).toEqual({className: "number react-number noselect"});
});


test('WheelChart fillChart', () => {
    const drawing = {lineWidth: 11, beginPath: jest.fn(), arc: jest.fn(), stroke: jest.fn()};
    const drawChart = jest.fn();
    const canvas = {getContext: jest.fn(() => drawing), width: 23, height: 113};

    class MockWheelChart extends WheelChart {

        drawChart () {
            drawChart.apply(this, arguments);
        }

        get canvas () {
            return canvas;
        }

        get drawing () {
            return drawing;
        }
    }

    let chart = shallow(<MockWheelChart />);
    chart.instance().fillChart(23, 113, 'purple');

    expect(drawing.beginPath.mock.calls).toEqual([[]]);
    expect(drawing.arc.mock.calls).toEqual([
        [23 / 2,
         113 / 2,
         chart.instance().radius,
         23 * Math.PI,
         113 * Math.PI]]);
    expect(drawing.strokeStyle).toBe('purple');
    expect(drawing.stroke.mock.calls).toEqual([[]]);
});


test('WheelChart drawChart', () => {
    const canvas = {width: 17, height: 43};
    const drawing = {clearRect: jest.fn(), arc: jest.fn(), stroke: jest.fn()};
    const fillChart = jest.fn();

    class MockWheelChart extends WheelChart {

        get canvas () {
            return canvas;
        }

        get drawing () {
            return drawing;
        }

        componentDidMount () {
            return;
        }

        fillChart (start, end, color) {
            fillChart(start, end, color);
        }
    }
    const data = [
        {value: 1, color: 'foo'},
        {value: undefined},
        {value: 2, color: 'bar'},
        {value: 3, color: 'baz'}];
    let chart = shallow(
        <MockWheelChart
           data={data}
           total={113} />);
    chart.instance().drawChart();

    expect(drawing.clearRect.mock.calls).toEqual([[0, 0, 17, 43]]);
    expect(drawing.lineWidth).toBe(3);
    expect(fillChart.mock.calls).toEqual(
        [[-0.5, -0.4823008849557522, "foo"],
         [-0.4823008849557522, -0.4469026548672566, "bar"],
         [-0.4469026548672566, -0.3938053097345132, "baz"]]);
});
