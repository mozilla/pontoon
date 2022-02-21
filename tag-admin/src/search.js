import React from 'react';

export const TagResourceSearch = ({ onSearch, onType }) => (
    <div
        className='container'
        style={{ content: '', display: 'table', width: '100%' }}
    >
        <div
            style={{
                float: 'left',
                boxSizing: 'border-box',
                width: '60%',
            }}
        >
            <div className='column'>
                <input
                    type='text'
                    className='search-tag-resources'
                    name='search'
                    onChange={(ev) => onSearch(ev.target.value)}
                    placeholder='Search for resources'
                />
            </div>
        </div>
        <div
            style={{
                float: 'left',
                boxSizing: 'border-box',
                width: '40%',
            }}
        >
            <div className='column'>
                <select
                    className='search-tag-resource-type'
                    name='type'
                    onChange={(ev) => onType(ev.target.value)}
                >
                    <option value='assoc'>Linked</option>
                    <option value='nonassoc'>Not linked</option>
                </select>
            </div>
        </div>
    </div>
);
