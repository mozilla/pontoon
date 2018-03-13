
import React from 'react';

import './wheel.css';


export default class WheelChart extends React.PureComponent {

    constructor (props) {
        super(props);
        this.canvas;
    }

    componentDidMount () {
        this.drawChart();
    }

    componentDidUpdate () {
        this.drawChart();
    }

    get canvasClassName () {
        return this.props.canvasClassName || "drawing";
    }

    get className () {
        return this.props.className || "wheel-chart";
    }

    get drawing () {
        return this.canvas.getContext('2d');
    }

    get height () {
        return this.props.height || '130px';
    }

    get percentageClassName () {
        return this.props.percentageClassName || 'number react-number noselect';
    }

    get radius () {
        return (this.canvas.width - this.drawing.lineWidth) / 2;
    }

    get width () {
        return this.props.width || '130px';
    }

    get x () {
        return this.canvas.width / 2;
    }

    get y () {
        return this.canvas.height / 2;
    }

    drawChart () {
        // Clear old canvas content to avoid aliasing
        this.drawing.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawing.lineWidth = 3;
        let start = -.5;
        let end, length;
        Object.entries(this.props.data).forEach(([, v]) => {
            if (!v.value) {
                return;
            }
            length = v.value / this.props.total * 2;
            end = start + length;
            this.fillChart(start, end, v.color);
            start = end;
        });
    }

    fillChart (start, end, color) {
        this.drawing.beginPath();
        this.drawing.arc(
            this.x,
            this.y,
            this.radius,
            start * Math.PI,
            end * Math.PI);
        this.drawing.strokeStyle = color;
        this.drawing.stroke();
    }

    render () {
        return (
            <div className={this.className}>
                {this.renderCanvas()}
                {this.renderPercentage()}
            </div>
        );
    }

    renderCanvas () {
        return (
            <canvas
               ref={(el) => this.canvas = el}
              className={this.canvasClassName}
              height={this.height}
              width={this.width}>
            </canvas>);
    }

    renderPercentage () {
        return (
            <span className={this.percentageClassName}>
              {this.props.percentage}
            </span>);
    }
}
