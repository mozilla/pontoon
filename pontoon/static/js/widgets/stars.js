
import React from 'react';

import './stars.css';

import {Icon} from 'widgets/icons';


export class Star extends React.PureComponent {

    get className () {
        return !this.props.className ? "star" : "star " + this.props.className;
    }

    render () {
        return (
            <Icon
               name="star"
               className={this.className} />);
    }
}


export class Stars extends React.PureComponent {

    render () {
        let stars = this.props.stars;
        if (this.props.total && this.props.total > this.props.stars) {
            stars = this.props.total;
        }
	return (
            <span className="stars">
              {Array(stars || 0).fill().map((_, k) => {
                  let className = '';
                  if (this.props.stars > k) {
                      className = "active";
                  }
                  return <Star key={k} className={className} />;
              })}
            </span>);
    }
}
