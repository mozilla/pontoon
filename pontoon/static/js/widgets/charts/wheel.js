
import React from 'react';

import './wheel.css';


export default class WheelChart extends React.PureComponent {
    canvasClassName = "drawing";
    className = "wheel-chart";
    height = '130px'
    percentageClassName = 'number react-number noselect';
    width = '130px'

    componentDidMount () {
        this.drawChart();
    }

    componentDidUpdate () {
        this.drawChart();
    }

    get drawing () {
        return this.canvas.getContext('2d');
    }

    get radius () {
        return (this.canvas.width - this.drawing.lineWidth) / 2;
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
            this.canvas.width / 2,
            this.canvas.height / 2,
            this.radius,
            start * Math.PI,
            end * Math.PI);
        this.drawing.strokeStyle = color;
        this.drawing.stroke();
    }

    render () {
        return (
            <div className={this.props.className || this.className}>
              {this.renderCanvas()}
              {this.renderPercentage()}
            </div>
        );
    }

    renderCanvas () {
        return (
            <canvas
               ref={(el) => this.canvas = el}
               key={0}
               className={this.props.canvasClassName || this.canvasClassName}
               height={this.props.height || this.height}
               width={this.props.width || this.width}>
            </canvas>);
    }

    renderPercentage () {
        return (
            <span key={1} className={this.props.percentageClassName || this.percentageClassName}>
              {this.props.percentage}
            </span>);
    }
}
