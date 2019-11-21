import React from 'react';

import './EditorLoader.css';

const list = [...Array(40).keys()];

export default function EditorLoader () {
    return <section className="entity-details editor-loader"> 
        <section className="main-column">
            <div className="entity-navigation"></div>
            <div className="metadata">
                <p className="original"></p>
                <p className="text-2"></p>
            </div>
            <div className="editor"></div>
            <div className="history">
                { list.map((i) => {
                    return <p className="text-2" key={ i }></p>
                }) }
            </div>
        </section>
        <section className="third-column">
            <div className="entity-navigation"></div>
                { list.map((i) => {
                    return <p className="original" key={ i }></p>
                }) }
        </section>
    </section>
}
