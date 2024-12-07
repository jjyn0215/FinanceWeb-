import React, { useState, useEffect, useRef } from "react";
import Stack from "@mui/material/Stack";
import NotificationsRoundedIcon from "@mui/icons-material/NotificationsRounded";
import MenuButton from "./MenuButton";
import ColorModeIconDropdown from "../theme/ColorModeIconDropdown";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import { useParams } from "react-router-dom";
import Search from "./Search";
import Chip from "@mui/material/Chip";
import io from "socket.io-client";
import { enqueueSnackbar, closeSnackbar } from "notistack";
import Skeleton from "@mui/material/Skeleton";
import SideMenuMobile from './SideMenuMobile';
import MenuRoundedIcon from '@mui/icons-material/MenuRounded';

export default function Header() {
  const theme = useTheme();
  const { ticker : subPath } = useParams();
  const [initialData, setData] = useState();
  const [afterData, setAfterData] = useState();
  const [longName, setLongName] = useState();
  const [diff, setDiff] = useState();
  const [diff2, setDiff2] = useState();
  const [loading, setLoading] = useState();
  const [isAfter, setIsAfter] = useState();

  const [open, setOpen] = React.useState(false);

  const toggleDrawer = function(newOpen) {
    return function() {
      setOpen(newOpen);
    };
  };
  
  useEffect(() => {
    fetch('/api/add', {
      method: 'POST',
      credentials: 'include', // 쿠키 포함
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ticker: subPath,
      }),
    })
      .then(() => {})
      .catch((err) => console.error(err));
    // WebSocket 연결 설정
    const socket = io("/chart");

    socket.on("connect", () => {
      console.log("헤더 열림!");
      socket.emit("join", subPath);
      enqueueSnackbar("헤더 연결 활성화됨", {
        variant: "success",
        autoHideDuration: 2000,
        preventDuplicate: true,
      });
    });

    socket.on("disconnect", () => {
      console.warn("헤더 닫힘!!");
    });

    socket.on("header", (data) => {
      console.log("받음!!!!!!!!!!!");
      const header = JSON.parse(data);
      console.log(header["%"].toFixed(2));
      setLongName(header["name"]);
      setData(header["current"].toFixed(2));
      setAfterData(header["afterClosed"].toFixed(2));
      setIsAfter(header["isAfter"]);
      if (header["diff"] > 0) {
        setDiff("+" + header["diff"].toFixed(2));
        setTrend("up");
        setTrendValues("+" + header["%"].toFixed(2) + "%");
      } else {
        setDiff(header["diff"].toFixed(2));
        setTrend("down");
        setTrendValues(header["%"].toFixed(2) + "%");
      }
      if (header["diff2"] > 0) {
        setDiff2("+" + header["diff2"].toFixed(2));
        setAfterTrend("up");
        setAfterTrendValues("+" + header["%2"].toFixed(2) + "%");
      } else {
        setDiff2(header["diff2"].toFixed(2));
        setAfterTrend("down");
        setAfterTrendValues(header["%2"].toFixed(2) + "%");
      }
      setLoading(1);
    });

    socket.on("name", (data) => {
      console.log("이름 받음");
      setLongName(data);
      })

    return () => {
      socket.close();
    };
  }, []);

  const labelColors = {
    up: "success",
    down: "error",
    neutral: "default",
  };
  const trendColors = {
    up:
      theme.palette.mode === "light"
        ? theme.palette.success.main
        : theme.palette.success.dark,
    down:
      theme.palette.mode === "light"
        ? theme.palette.error.main
        : theme.palette.error.dark,
    neutral:
      theme.palette.mode === "light"
        ? theme.palette.grey[400]
        : theme.palette.grey[700],
  };
  const [trend, setTrend] = useState("neutral");
  const [afterTrend, setAfterTrend] = useState("neutral");

  const color = labelColors[trend];
  const color2 = labelColors[afterTrend];
  const diffColor = trendColors[trend];
  const diffColor2 = trendColors[afterTrend];
  const [trendValues, setTrendValues] = useState("0%");
  const [afterTrendValues, setAfterTrendValues] = useState("0%");

  return (
    <Stack
      direction="row"
      sx={{
        display: { xs: "auto", md: "flex" },
        width: "100%",
        alignItems: { xs: "flex-start", md: "center" },
        justifyContent: "space-between",
        maxWidth: { sm: "100%", md: "4000px" },
        pt: 1.5,
      }}
      spacing={2}
    >
      {loading ? (
        <Stack direction="row" sx={{ gap: 1 }}>
          <Typography variant="h4" sx={{ mr: 1 }}>
            {subPath}
          </Typography>
          <Typography
            variant="h4"
            sx={{ mr: 2, display: { xs: "none", md: "flex" } }}
          >
            - {longName}
          </Typography>
          <Typography variant="h5" sx={{ mt: 0.6 }}>
            {initialData}
          </Typography>
          <Typography variant="h5" sx={{ mt: 0.6, color: diffColor }}>
            {diff}
          </Typography>
          <Chip
            size="small"
            color={color}
            label={trendValues}
            sx={{ mt: 1.2, mr: 4 }}
          />
          {isAfter ? (
            <React.Fragment>
              <Typography variant="h5" sx={{ mt: 0.6 }}>
                {afterData}
              </Typography>
              <Typography variant="h5" sx={{ mt: 0.6, color: diffColor2 }}>
                {diff2}
              </Typography>
              <Chip
                size="small"
                color={color2}
                label={afterTrendValues}
                sx={{ mt: 1.2 }}
              />
            </React.Fragment>
          ) : null}
        </Stack>
      ) : (
        <Skeleton variant="rounded" width={650} height={36} />
      )}

      <Stack direction="row" sx={{ gap: 1 }}>
        <Search />
        <ColorModeIconDropdown />
        <MenuButton aria-label="menu" onClick={toggleDrawer(true)}>
            <MenuRoundedIcon />
          </MenuButton>
          <SideMenuMobile open={open} toggleDrawer={toggleDrawer} />
      </Stack>
    </Stack>
  );
}
