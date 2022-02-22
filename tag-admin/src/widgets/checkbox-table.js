import React, { useCallback, useEffect, useRef, useState } from 'react';
import ReactTable from 'react-table';

import 'react-table/react-table.css';

import { Checkbox } from './checkbox.js';

// Returns a copy of the `checked` set with only resource paths that are in `visible`
const prune = (checked, visible) =>
  new Set([...checked].filter((v) => visible.includes(v)));

export function CheckboxTable({ data, onSubmit, submitMessage }) {
  const visible = useRef([]);
  const [checked, setChecked] = useState(new Set());
  const clearChecked = () => setChecked(new Set());
  const pruneChecked = () =>
    setChecked((checked) => prune(checked, visible.current));

  useEffect(() => {
    visible.current.length = 0;
    clearChecked();
  }, [data]);

  const selectAll = useCallback(() => {
    setChecked((checked) => {
      if (checked.size > 0) return new Set();
      else return new Set([...visible.current.filter(Boolean)]);
    });
  }, []);

  const selectOne = useCallback(({ target }) => {
    setChecked((checked) => {
      const next = new Set(checked);
      if (target.checked) next.add(target.name);
      else next.delete(target.name);
      return next;
    });
  }, []);

  const Header = () => {
    const pruned = prune(checked, visible.current);
    // some rows can be empty strings if there are more visible rows than resources
    const some = pruned.size > 0;
    const all = some && pruned.size === visible.current.filter(Boolean).length;

    return (
      <Checkbox
        checked={all}
        indeterminate={some && !all}
        onChange={selectAll}
      />
    );
  };

  const Cell = (item) => {
    const name = item.original[0];
    visible.current.length = item.pageSize;
    visible.current[item.viewIndex] = name;

    return (
      <Checkbox checked={checked.has(name)} name={name} onChange={selectOne} />
    );
  };

  const columns = [
    { Header, Cell, sortable: false, width: 45 },
    {
      Header: 'Resource',
      id: 'type',
      Cell: (item) => <span>{item.original[0]}</span>,
    },
  ];

  const handleSubmit = async (evt) => {
    // after emitting handleSubmit to parent with list of currently
    // checked, clears the checkboxes
    evt.preventDefault();
    await onSubmit({ data: [...checked] });
    clearChecked();
  };

  return (
    <div>
      <ReactTable
        defaultPageSize={5}
        className='-striped -highlight'
        data={data}
        onPageChange={() => {
          visible.current.length = 0;
          clearChecked();
        }}
        onPageSizeChange={(pageSize) => {
          visible.current.length = pageSize;
          pruneChecked();
        }}
        onSortedChange={pruneChecked}
        columns={columns}
      />
      <button className='tag-resources-associate' onClick={handleSubmit}>
        {submitMessage}
      </button>
    </div>
  );
}
