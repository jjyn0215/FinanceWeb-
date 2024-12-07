import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Checkbox from '@mui/material/Checkbox';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormLabel from '@mui/material/FormLabel';
import FormControl from '@mui/material/FormControl';
import Link from '@mui/material/Link';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import MuiCard from '@mui/material/Card';
import { styled } from '@mui/material/styles';
import AppTheme from '../theme/AppTheme';
import { GoogleIcon, FacebookIcon, SitemarkIcon } from './CustomIcons';
import ColorModeSelect from '../theme/ColorModeSelect';
import { useNavigate } from 'react-router-dom';
import { enqueueSnackbar, closeSnackbar } from "notistack";

const Card = styled(MuiCard)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignSelf: 'center',
  width: '100%',
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  margin: 'auto',
  boxShadow:
    'hsla(220, 30%, 5%, 0.05) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.05) 0px 15px 35px -5px',
  [theme.breakpoints.up('sm')]: {
    width: '450px',
  },
  ...theme.applyStyles('dark', {
    boxShadow:
      'hsla(220, 30%, 5%, 0.5) 0px 5px 15px 0px, hsla(220, 25%, 10%, 0.08) 0px 15px 35px -5px',
  }),
}));

const SignUpContainer = styled(Stack)(({ theme }) => ({
  height: 'calc((1 - var(--template-frame-height, 0)) * 100dvh)',
  minHeight: '100%',
  padding: theme.spacing(2),
  [theme.breakpoints.up('sm')]: {
    padding: theme.spacing(4),
  },
  '&::before': {
    content: '""',
    display: 'block',
    position: 'absolute',
    zIndex: -1,
    inset: 0,
    backgroundImage:
      'radial-gradient(ellipse at 50% 50%, hsl(210, 100%, 97%), hsl(0, 0%, 100%))',
    backgroundRepeat: 'no-repeat',
    ...theme.applyStyles('dark', {
      backgroundImage:
        'radial-gradient(at 50% 50%, hsla(210, 100%, 16%, 0.5), hsl(220, 30%, 5%))',
    }),
  },
}));

export default function SignUp(props) {
    const [emailError, setEmailError] = useState(false);
    const [emailErrorMessage, setEmailErrorMessage] = useState('');
    const [passwordError, setPasswordError] = useState(false);
    const [passwordErrorMessage, setPasswordErrorMessage] = useState('');
    const [nameError, setNameError] = useState(false);
    const [nameErrorMessage, setNameErrorMessage] = useState('');
    const navigate = useNavigate();
  
    const validateInputs = () => {
      const email = document.getElementById('email');
      const password = document.getElementById('password');
      const name = document.getElementById('name');
  
      let isValid = true;
  
      if (!email.value || !/\S+@\S+\.\S+/.test(email.value)) {
        setEmailError(true);
        setEmailErrorMessage('유효한 이메일 주소를 입력하세요,');
        isValid = false;
      } else {
        setEmailError(false);
        setEmailErrorMessage('');
      }
  
      if (!password.value || password.value.length < 8) {
        setPasswordError(true);
        setPasswordErrorMessage('비밀번호는 8자리 이상이어야 합니다.');
        isValid = false;
      } else {
        setPasswordError(false);
        setPasswordErrorMessage('');
      }
  
      if (!name.value || name.value.length < 1) {
        setNameError(true);
        setNameErrorMessage('이름 쓰세요 !!!');
        isValid = false;
      } else {
        setNameError(false);
        setNameErrorMessage('');
      }
  
      return isValid;
    };
  
    useEffect(() => {
      closeSnackbar('offline');
      fetch('/api/protected', {
        method: 'GET',
        credentials: 'include', // 쿠키 포함
      })
        .then((response) => {
          if (response.ok) {
            navigate("/Chart/005930.KS");
            return response.json();
          } else {
            throw new Error('Unauthorized');
          }
        })
        .then((data) => console.log(data))
        .catch((err) => console.error(err));
    });

    const handleSubmit = async (event) => {
      event.preventDefault();
      if (!validateInputs()) return; 

      const data = new FormData(event.currentTarget);
      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: data.get('name'),
            email: data.get('email'),
            password: data.get('password'),
          }),
        });
    
        if (response.ok) {
          navigate('/SignIn', { state:  { status: "new SignUp", message: "회원가입 성공! 로그인이 필요합니다." }}); // React Router 사용 시
        } else {
          const errorData = await response.json();
          if (errorData.message === "Email already exists") {
            setEmailError(true);
            setEmailErrorMessage("이미 존재하는 이메일입니다.");
          }
        }
      } catch (error) {
        console.error('Error:', error, );
        alert('An error occurred while signing up.');
      }
    };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <ColorModeSelect sx={{ position: 'fixed', top: '1rem', right: '1rem' }} />
      <SignUpContainer direction="column" justifyContent="space-between">
        <Card variant="outlined">
          <Typography
            component="h1"
            variant="h4"
            sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.15rem)' }}
          >
            회원가입
          </Typography>
          <Box
            component="form"
            method='post'
            noValidate
            onSubmit={handleSubmit}
            sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
          >
            <FormControl>
              <FormLabel htmlFor="name">이름 또는 닉네임</FormLabel>
              <TextField
                autoComplete="name"
                name="name"
                required
                fullWidth
                id="name"
                placeholder="홍길동"
                error={nameError}
                helperText={nameErrorMessage}
                color={nameError ? 'error' : 'primary'}
              />
            </FormControl>
            <FormControl>
              <FormLabel htmlFor="email">이메일</FormLabel>
              <TextField
                required
                fullWidth
                id="email"
                placeholder="example@email.com"
                name="email"
                autoComplete="email"
                variant="outlined"
                error={emailError}
                helperText={emailErrorMessage}
                color={passwordError ? 'error' : 'primary'}
              />
            </FormControl>
            <FormControl>
              <FormLabel htmlFor="password">비밀번호</FormLabel>
              <TextField
                required
                fullWidth
                name="password"
                placeholder="••••••••"
                type="password"
                id="password"
                autoComplete="new-password"
                variant="outlined"
                error={passwordError}
                helperText={passwordErrorMessage}
                color={passwordError ? 'error' : 'primary'}
              />
            </FormControl>
            {/* <FormControlLabel
              control={<Checkbox value="allowExtraEmails" color="primary" />}
              label="I want to receive updates via email."
            /> */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              onClick={validateInputs}
            >
              등록!
            </Button>
          </Box>
          <Divider>
          </Divider>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* <Button
              fullWidth
              variant="outlined"
              onClick={() => alert('Sign up with Google')}
              startIcon={<GoogleIcon />}
            >
              Sign up with Google
            </Button>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => alert('Sign up with Facebook')}
              startIcon={<FacebookIcon />}
            >
              Sign up with Facebook
            </Button> */}
            <Typography sx={{ textAlign: 'center' }}>
              계정이 이미 있나요?{' '}
              <Link
                href="/SignIn/"
                variant="body2"
                sx={{ alignSelf: 'center' }}
              >
                로그인하기
              </Link>
            </Typography>
          </Box>
        </Card>
      </SignUpContainer>
    </AppTheme>
  );
}
