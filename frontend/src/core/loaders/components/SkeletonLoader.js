import React from 'react';

import './SkeletonLoader.css';

export default function SkeletonLoader(props) {
    const firstLoad = props.entities.length === 0;
    const entityCount = firstLoad ? 30 : 2;
    const list = [...Array(entityCount).keys()];

    return (
        <ul
            className={`skeleton-loader entities ${
                firstLoad ? null : 'scroll'
            }`}
        >
            {list.map((i) => {
                const classes = `entity missing ${
                    i === 0 && firstLoad ? 'selected' : null
                }`;
                return (
                    <li className={classes} key={i}>
                        <span className='status fa' />
                        <div>
                            <p className='source-string'></p>
                            <p className='text-2'></p>
                        </div>
                    </li>
                );
            })}
        </ul>
    );
}
