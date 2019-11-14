import React from 'react';
import { connect } from 'react-redux';

import './SkeletonLoader.css';

import * as entities from 'core/entities';

import type { EntitiesState } from 'core/entities';

type Props = {|
    entities: EntitiesState
|};

const list = [...Array(30).keys()];

const SkeletonLoader = (props) => {
    return ( props.entities.entities.length === 0 ?
        <ul className='skeleton-loader entities'>
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
        :
        // Loader to use after the first load.
        <h3 className="loading">
            <div className="fa fa-sync fa-spin"></div>
        </h3> 
    )
}

const mapStateToProps = (state: Object): Props => {
    return {
        entities: state[entities.NAME]
    };
};

export default connect(mapStateToProps)(SkeletonLoader);
