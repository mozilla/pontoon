
import React from 'react';


export class Section extends React.PureComponent {

    get className () {
        return this.props.className || 'wrapper';
    }

    render () {
        return (
            <section id={this.props.id}>
              <div className={this.className}>
                {this.props.children}
              </div>
            </section>);
    }
}
