import React, { useCallback, useEffect, useState } from 'react';

import { TagResourceSearch } from './search.js';
import { post } from './utils/http-post.js';
import { CheckboxTable } from './widgets/checkbox-table.js';
import { ErrorList } from './widgets/error-list.js';

import './tag-resources.css';

export function TagResourceManager({ api }) {
  const [data, setData] = useState([]);
  const [errors, setErrors] = useState({});
  const [type, setType] = useState('assoc');
  const [search, setSearch] = useState('');

  const handleChange = useCallback(
    async (params) => {
      const response = await post(api, params);
      const json = await response.json();
      if (response.status === 200) {
        setData(json.data || []);
        setErrors({});
      } else {
        setErrors(json.errors || {});
      }
    },
    [api],
  );

  useEffect(() => {
    handleChange({ search, type });
  }, [search, type]);

  const message = type === 'assoc' ? 'Unlink resources' : 'Link resources';
  return (
    <div className='tag-resource-widget'>
      <TagResourceSearch onSearch={setSearch} onType={setType} />
      <ErrorList errors={errors} />
      <CheckboxTable
        data={data}
        onSubmit={({ data }) => handleChange({ data, search, type })}
        submitMessage={message}
      />
    </div>
  );
}
