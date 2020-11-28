import React from 'react';

export class Columns extends React.PureComponent {
    render() {
        return (
            <Container
                columns={this.props.columns.length}
                ratios={this.props.columns.map(([, v]) => v)}
            >
                {this.props.columns.map(([column], key) => {
                    return <Column key={key}>{column}</Column>;
                })}
            </Container>
        );
    }
}

export class Container extends React.Component {
    createColumnStyle(width) {
        return {
            float: 'left',
            boxSizing: 'border-box',
            width: width.toString() + '%',
        };
    }

    get containerStyle() {
        return {
            content: '',
            display: 'table',
            width: '100%',
        };
    }

    get columnStyles() {
        let { columns, ratios } = this.props;
        let result = [];
        ratios = ratios || [];
        if (!columns) {
            return result;
        }
        if (ratios.length) {
            // sum of rations
            const total = ratios.reduce((a, b) => a + b, 0);
            // percentage widths of each column
            const widths = ratios.map((column) => (column / total) * 100);
            // give each column the correct width
            widths.map((width) => result.push(this.createColumnStyle(width)));
            return result;
        } else {
            // give each column an equal share
            return [
                ...Array(columns)
                    .fill()
                    .map(() => this.createColumnStyle(100 / columns)),
            ];
        }
    }

    render() {
        let { children } = this.props;
        return (
            <div className='container' style={this.containerStyle}>
                {React.Children.map(children || [], (child, key) => {
                    let columnStyle = {};
                    if (this.columnStyles.length >= key) {
                        columnStyle = this.columnStyles[key];
                    }
                    return (
                        <div key={key} style={columnStyle || {}}>
                            {child}
                        </div>
                    );
                })}
            </div>
        );
    }
}

export class Column extends React.PureComponent {
    render() {
        const { className } = this.props;
        let _className = 'column';
        if (className) {
            _className = _className + ' ' + className;
        }
        return <div className={_className}>{this.props.children}</div>;
    }
}
