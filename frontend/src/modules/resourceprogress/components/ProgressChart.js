/* @flow */

import * as React from 'react';

import './ProgressChart.css';

import type { Stats } from 'core/stats';

type Props = {|
    stats: Stats,
    size: number,
|};

/**
 * Render current resource progress data on canvas.
 */
export default class ProgressChart extends React.Component<Props> {
    canvas: { current: HTMLCanvasElement | null };

    constructor(props: Props) {
        super(props);
        this.canvas = React.createRef();
    }

    componentDidMount() {
        this.setUpCanvas();
        this.drawCanvas();
    }

    componentDidUpdate() {
        this.drawCanvas();
    }

    setUpCanvas() {
        const dpr = window.devicePixelRatio || 1;
        const canvas = this.canvas.current;

        if (!canvas) {
            return;
        }

        // Set up canvas to be HiDPI display ready
        canvas.style.width = canvas.width + 'px';
        canvas.style.height = canvas.height + 'px';
        canvas.width = canvas.width * dpr;
        canvas.height = canvas.height * dpr;
    }

    drawCanvas() {
        const {
            approved,
            fuzzy,
            warnings,
            errors,
            missing,
            total,
        } = this.props.stats;
        const dpr = window.devicePixelRatio || 1;
        const canvas = this.canvas.current;

        const data = [
            {
                type: total ? approved / total : 0,
                color: '#7BC876',
            },
            {
                type: total ? fuzzy / total : 0,
                color: '#FED271',
            },
            {
                type: total ? warnings / total : 0,
                color: '#FFA10F',
            },
            {
                type: total ? errors / total : 0,
                color: '#F36',
            },
            {
                type: total ? missing / total : 0,
                color: '#5F7285',
            },
        ];

        if (!canvas) {
            return;
        }

        const context = canvas.getContext('2d');

        // Clear old canvas content to avoid aliasing
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.lineWidth = 3 * dpr;

        const x = canvas.width / 2;
        const y = canvas.height / 2;
        const radius = (canvas.width - context.lineWidth) / 2;
        let end = null;

        data.forEach((item) => {
            const length = item.type * 2;
            const start = end !== null ? end : -0.5;
            end = start + length;

            context.beginPath();
            context.arc(x, y, radius, start * Math.PI, end * Math.PI);
            context.strokeStyle = item.color;
            context.stroke();
        });
    }

    render() {
        return (
            <canvas
                ref={this.canvas}
                height={this.props.size}
                width={this.props.size}
            />
        );
    }
}
