import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Drawer, { drawerClasses } from '@mui/material/Drawer';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import LogoutRoundedIcon from '@mui/icons-material/LogoutRounded';
import NotificationsRoundedIcon from '@mui/icons-material/NotificationsRounded';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import { useNavigate } from 'react-router-dom';

import MenuButton from './MenuButton';
import MenuContent from './MenuContent';
import CardAlert from '../nousage/CardAlert';
import FocusTrap from '@mui/material/Unstable_TrapFocus';

function SideMenuMobile({ open, toggleDrawer }) {
  const navigate = useNavigate();
  const [userName, setUserName] = useState('???');
  const [recentStocks, setRecentStocks] = useState([]);
  const handleClick = () => {
    fetch('/api/logout', {
      method: 'POST',
      credentials: 'include', // 쿠키 포함
    })
      .then((response) => navigate("/SignIn", { state: { type: "logout", message: "로그아웃 되었습니다."}}))
      .then((data) => console.log(data))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    // WebSocket 연결 설정
    async function fecthData() {
      await fetch('/api/protected', {
        method: 'GET',
        credentials: 'include', // 쿠키 포함
      })
        .then(async (response) => {
          if (response.ok) {
            const data = await response.json();
            const combinedStocks = (data.ticker || []).map((ticker, index) => ({
              ticker,
              name: (data.name || [])[index] || '', // name이 없으면 빈 문자열 처리
            }));
            setRecentStocks(combinedStocks);
            setUserName(data.username);
          } else {
            navigate("/SignIn");
          }
        })
        .catch((err) => console.error(err));
    } 
    fecthData();
  }, [navigate]);

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={toggleDrawer(false)}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        [`& .${drawerClasses.paper}`]: {
          backgroundImage: 'none',
          backgroundColor: 'background.paper',
        },
      }}
    >
      <Stack
        sx={{
          maxWidth: '70dvw',
          height: '100%',
        }}
      >
        <Stack direction="row" sx={{ p: 2, pb: 0, gap: 1 }}>
          <Stack
            direction="row"
            sx={{ gap: 1, alignItems: 'center', flexGrow: 1, p: 1 }}
          >
            <Avatar
              sizes="small"
              alt={userName}
              src="/static/images/avatar/7.jpg"
              sx={{ width: 32, height: 32 }}
            />
            <Typography component="p" variant="h6">
              {userName}
            </Typography>
          </Stack>

        </Stack>
        <Divider />
        <Stack sx={{ flexGrow: 1, overflow: 'auto' }}>
          <List>
            {recentStocks.map((stock, index) => (
              <ListItem
                key={index}
                button
                onClick={() => navigate(`/Chart/${stock.ticker}`)}
              >
 
                <ListItemText
                  primary={stock.ticker}
                  secondary={stock.name}
                />
              </ListItem>
            ))}
          </List>
          <Divider />
        </Stack>
        <Stack sx={{ p: 2 }}>
          <Button variant="outlined" fullWidth startIcon={<LogoutRoundedIcon />} onClick={handleClick}>
            로그아웃
          </Button>
        </Stack>
      </Stack>
    </Drawer>
  );
}

SideMenuMobile.propTypes = {
  open: PropTypes.bool,
  toggleDrawer: PropTypes.func.isRequired,
};

export default SideMenuMobile;
