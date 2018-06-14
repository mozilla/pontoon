import React from 'react';


class Entity extends React.Component {
    get status() {
        const { entity } = this.props;
        const translation = entity.translation[0];

        if (translation.approved) {
            return 'approved';
        }
        if (translation.fuzzy) {
            return 'fuzzy';
        }
        return 'missing';
    }

    render() {
        const { entity, selectEntity } = this.props;

        return (
            <li className={ `entity ${this.status}` } onClick={ selectEntity }>
                <span className='status fa' />
                <span className='source-string'>{ entity.original }</span>
                <span className='translation-string'>{ entity.translation[0].string }</span>
            </li>
        );
    }
}


export default class EntitiesList extends React.Component {
    render() {
        const { entities, selectEntity } = this.props;

        return (
            <ul className='entities'>
                { entities.map((entity, i) => {
                    return <Entity
                        entity={ entity }
                        selectEntity={ selectEntity }
                        key={ i }
                    />;
                }) }
            </ul>
        );
    }
}
