import React, { useState, useEffect, useRef } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid2";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import InsightsRoundedIcon from "@mui/icons-material/InsightsRounded";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import FinanceChart from "./Chart";
import { useParams } from "react-router-dom";
import io from "socket.io-client"
import { enqueueSnackbar, closeSnackbar } from 'notistack';

export default function Home() {
  const theme = useTheme();
  const colorPalette = [
    theme.palette.primary.light,
    theme.palette.primary.main,
    theme.palette.primary.dark,
  ];
  
  return (
    <Box sx={{ width: "100%", maxWidth: { sm: "100%", md: "4000px" } }}>
      <Grid
        container
        spacing={2}
        columns={12}
        sx={{ mb: (theme) => theme.spacing(2) }}
      >
          <FinanceChart />
      </Grid>
    </Box>
  );
}
