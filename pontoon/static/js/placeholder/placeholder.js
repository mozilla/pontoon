
import React from 'react';


export default class Placeholder extends React.Component {

    render () {
        return <div />
    }

}

const foo = {}
const bar = {baz: 23}

Object.assign(foo, bar)

const baz = new Map({...foo})
baz;
const placeholder = new Placeholder()
placeholder;
const promise = Promise.resolve('boom')

promise().then(result => {
    result
})
