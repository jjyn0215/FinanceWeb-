import React, { useState, useEffect } from 'react';
import FormControl from '@mui/material/FormControl';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import { replace, useNavigate  } from 'react-router-dom';
import { useFormControl } from '@mui/material/FormControl';


export default function Search() {
  const navigate = useNavigate();
  const [value, setValue] = useState('');

  const handleKeyDown = async (event) => {
    if (event.key === 'Enter' && value.trim() !== '') {
      navigate(`/Chart/${value}`); 
    }
  };

  const handleChange = (event) => {
    setValue(event.target.value); // 입력 값 업데이트
  };

  return (
    <FormControl sx={{ width: { xs: '100%', md: '25ch' }, display:{xs: 'none', md: 'flex'} }} variant="outlined">
      <OutlinedInput
        size="small"
        id="search"
        placeholder="이동"
        sx={{ flexGrow: 1 }}
        onChange={handleChange} // 값 업데이트
        onKeyDown={handleKeyDown} // Enter 키 이벤트 처리
        startAdornment={
          <InputAdornment position="start" sx={{ color: 'text.primary' }}>
            <SearchRoundedIcon fontSize="small" />
          </InputAdornment>
        }
        inputProps={{
          'aria-label': 'search',
        }}
      />
    </FormControl>
  );
}
