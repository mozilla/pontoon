import React from 'react';

import './SkeletonLoader.css';

const list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

const SkeletonLoader = () => (
    <div className="skeleton-loader entities unselectable">
        <ul>
            { list.map((i) => {
                const classes = `entity missing ${i ===1 ? 'selected' : null}`
                return <li className={ classes }>
                    <span className='status fa'/>
                    <div>
                        <p className='source-string'></p>
                        <p className='text-2'></p>
                    </div>
                </li>
            }) }
        </ul>
    </div>
);

export default SkeletonLoader;
