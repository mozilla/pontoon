
import React from 'react';


export class Section extends React.PureComponent {
    className = 'wrapper';

    render () {
        return (
            <section id={this.props.id}>
              <div className={this.props.className || this.className}>
                {this.props.children}
              </div>
            </section>);
    }
}
