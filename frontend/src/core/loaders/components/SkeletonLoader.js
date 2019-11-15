import React from 'react';

import './SkeletonLoader.css';

let list;

export default function SkeletonLoader (props) {
    { list = props.entities.length === 0 ? [...Array(30).keys()] : [...Array(2).keys()] }
    return <ul className={`skeleton-loader entities ${props.entities.length === 0 ? 'entities' : 'loading'}`}>
        { list.map((i) => {
            const classes = `entity missing ${i === 0 ? 'selected' : null}`
            return <li className={ classes } key={ i }>
                <span className='status fa'/>
                <div>
                    <p className='source-string'></p>
                    <p className='text-2'></p>
                </div>
            </li>
        }) }
    </ul>
}
