import React from 'react';

import './SkeletonLoader.css';

const list = [...Array(30).keys()];

export default function SkeletonLoader () {
    return <ul className='skeleton-loader entities'>
        { list.map((i) => {
            const classes = `entity missing ${i === 0 ? 'selected' : null}`
            return <li className={ classes } key={ i }>
                <span className='status fa'/>
                <div>
                    <p className='source-string'></p>
                    <p className='translation-string'></p>
                </div>
            </li>
        }) }
    </ul>
}
