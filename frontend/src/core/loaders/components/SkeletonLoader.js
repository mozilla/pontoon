import React from 'react';

import './SkeletonLoader.css';

const list = [...Array(30).keys()];

const SkeletonLoader = () => (
    <div className='skeleton-loader entities'>
        <ul>
            { list.map((i) => {
                const classes = `entity missing ${i === 0 ? 'selected' : null}`
                return <li className={ classes }>
                    <span className='status fa'/>
                    <div>
                        <p className='source-string'></p>
                        <p className='translation-string'>meee</p>
                        <p className='text-2'></p>
                    </div>
                </li>
            }) }
        </ul>
    </div>
);

export default SkeletonLoader;
