import React, { useState, useEffect, useRef } from "react";
import ReactDOM from "react-dom";
import { format } from "d3-format";
import { timeFormat } from "d3-time-format";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Skeleton from "@mui/material/Skeleton";
import CircularProgress from "@mui/material/CircularProgress";
import { useParams } from "react-router-dom";
import io from "socket.io-client"
import { enqueueSnackbar, closeSnackbar } from 'notistack';
import { useTheme } from "@mui/material/styles";
import { useNavigate, useLocation } from "react-router-dom";
import {
  elderRay,
  ema,
  discontinuousTimeScaleProviderBuilder,
  Chart,
  ChartCanvas,
  CurrentCoordinate,
  BarSeries,
  CandlestickSeries,
  ElderRaySeries,
  LineSeries,
  MovingAverageTooltip,
  OHLCTooltip,
  SingleValueTooltip,
  lastVisibleItemBasedZoomAnchor,
  XAxis,
  YAxis,
  CrossHairCursor,
  EdgeIndicator,
  MouseCoordinateX,
  MouseCoordinateY,
  ZoomButtons,
  withDeviceRatio,
  withSize,
} from "react-financial-charts";
import { Global } from "@emotion/react";
//import { initialData } from "./Data";

const Mainchart = () => {
  const theme = useTheme();
  const [initialData, setData] = useState([{}]);
  const cardRef = useRef(null);
  const [width, setWidth] = useState();
  const [height, setHeight] = useState();
  const [loading, setLoading] = useState();
  const [offline, setOffline] = useState();
  const { ticker : subPath } = useParams();
  const navigate = useNavigate();
  const { state } = useLocation();

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

  useEffect(() => {
    // 차트 크기
    if (cardRef.current) {
      setWidth(cardRef.current.offsetWidth - 30);
      setHeight(window.innerHeight - 160);
    }
    const handleResize = () => {
      if (cardRef.current) {
        setWidth(cardRef.current.offsetWidth - 30);
        setHeight(window.innerHeight - 160);
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    // WebSocket 연결 설정
    if (state != null && state !== undefined){
      enqueueSnackbar(state?.message, {variant: 'info', autoHideDuration: 3000, preventDuplicate: true});
    }

    async function fecthData() {
      await fetch('/api/protected', {
        method: 'GET',
        credentials: 'include', // 쿠키 포함
      })
        .then(async (response) => {
          if (response.ok) {
          } else {
            navigate("/SignIn");
          }
        })
        .catch((err) => console.error(err));
    } 
    fecthData();
    const socket = io("/chart");

    socket.on("connect", () => {
      closeSnackbar('offline');
      console.log("열림!");
      socket.emit('join', subPath);
      enqueueSnackbar("차트 연결 활성화됨", {variant: 'success', autoHideDuration: 2000, preventDuplicate: true});
    });

    socket.on("disconnect", () => {
      console.warn("닫힘!!");
      closeSnackbar();
      enqueueSnackbar("서버와 연결 끊김", {variant: 'error', persist: true, preventDuplicate: true, key: 'offline'});
    });

    // socket.on("welcome", (addr) => {
    //   enqueueSnackbar("환영합니다, " + addr, {variant: 'info', autoHideDuration: 3000})
    // });

    socket.on("notFound", () => {
      fetch('/api/remove', {
        method: 'POST',
        credentials: 'include', // 쿠키 포함
        headers: {
          'Content-Type': 'application/json',
        },  
        body: JSON.stringify({
          ticker: subPath
        }),
      })
        .then((response) => {
          if (response.ok) {
          } else {
          }
        })
        .catch((err) => console.error(err));
      navigate("/404")
    });
    
    socket.on("chart", (chart) => {
      console.log("받음!")
      setData(JSON.parse(chart));
      console.log(JSON.parse(chart));
      setLoading(1);
    });

    return () => {
      socket.close();
    };
  }, []);

  const ScaleProvider =
    discontinuousTimeScaleProviderBuilder().inputDateAccessor(
      (d) => new Date(d.date)
    );

  const margin = { left: 0, right: 48, top: 0, bottom: 24 };
  
  
  const ema12 = ema()
    .id(1)
    .options({ windowSize: 12 })
    .merge((d, c) => {
      d.ema12 = c;
    })
    .accessor((d) => d.ema12);

  const ema26 = ema()
    .id(2)
    .options({ windowSize: 26 })
    .merge((d, c) => {
      d.ema26 = c;
    })
    .accessor((d) => d.ema26);

  const elder = elderRay();

  const calculatedData = loading && initialData.length > 0
  ? elder(ema26(ema12(initialData)))
  : {};
  const { data, xScale, xAccessor, displayXAccessor } =
    ScaleProvider(initialData);
  const pricesDisplayFormat = format(".2f");
  const max = xAccessor(data[data.length - 1]);
  const min = xAccessor(data[Math.max(0, data.length - 100)]);
  const xExtents = [min, max + 5];

  const gridHeight = height - margin.top - margin.bottom;

  const elderRayHeight = 100;
  const elderRayOrigin = (_, h) => [0, h - elderRayHeight];
  const barChartHeight = gridHeight / 4;
  const barChartOrigin = (_, h) => [0, h - barChartHeight - elderRayHeight];
  const chartHeight = gridHeight - elderRayHeight;
  const yExtents = (data) => {
    return [data.high, data.low];
  };
  const dateTimeFormat = "KST %m/%d %H:%M";
  const timeDisplayFormat = timeFormat(dateTimeFormat);

  const barChartExtents = (data) => {
    return data.volume;
  };

  const candleChartExtents = (data) => {
    return [data.high, data.low];
  };

  const yEdgeIndicator = (data) => {
    return data.close;
  };

  const volumeColor = (data) => {
    return data.close > data.open
      ? "rgba(38, 166, 154, 0.5)"
      : "rgba(239, 83, 80, 0.5)";
  };

  const volumeSeries = (data) => {
    return data.volume;
  };

  const openCloseColor = (data) => {
    return data.close > data.open ? "#26a69a" : "#ef5350";
  };

  return (
    <Card
      variant="outlined"
      ref={cardRef}
      sx={{ width: "100%", height: "100%" }}
    >
      <CardContent>
        {loading ? (
          <ChartCanvas
            height={height}
            ratio={3}
            width={width}
            margin={margin}
            data={data}
            displayXAccessor={displayXAccessor}
            seriesName="Data"
            xScale={xScale}
            xAccessor={xAccessor}
            xExtents={xExtents}
            zoomAnchor={lastVisibleItemBasedZoomAnchor}
            
          > 
            <Chart
              id={2}
              height={barChartHeight}
              origin={barChartOrigin}
              yExtents={barChartExtents}
            >
              <BarSeries fillStyle={volumeColor} yAccessor={volumeSeries} />
            </Chart>
            <Chart id={3} height={chartHeight} yExtents={candleChartExtents}>
              <XAxis showGridLines showTickLabel={false} />
              <YAxis showGridLines tickFormat={pricesDisplayFormat} tickLabelFill={theme.palette.text.primary} strokeStyle={theme.palette.text.primary}/>
              <CandlestickSeries />
              <LineSeries
                yAccessor={ema26.accessor()}
                strokeStyle={ema26.stroke()}
                
              />
              <CurrentCoordinate
                yAccessor={ema26.accessor()}
                fillStyle={ema26.stroke()}
                
              />
              <LineSeries
                yAccessor={ema12.accessor()}
                strokeStyle={ema12.stroke()}
              />
              <CurrentCoordinate
                yAccessor={ema12.accessor()}
                fillStyle={ema12.stroke()}
              />
              <MouseCoordinateY
                rectWidth={margin.right}
                displayFormat={pricesDisplayFormat}
              />
              <EdgeIndicator
                itemType="last"
                rectWidth={margin.right}
                fill={openCloseColor}
                lineStroke={openCloseColor}
                displayFormat={pricesDisplayFormat}
                yAccessor={yEdgeIndicator}
              />
              <MovingAverageTooltip
                origin={[8, 24]}
                textFill={theme.palette.text.primary}
                options={[
                  {
                    yAccessor: ema26.accessor(),
                    type: "EMA",
                    stroke: ema26.stroke(),
                    windowSize: ema26.options().windowSize,
                  },
                  {
                    yAccessor: ema12.accessor(),
                    type: "EMA",
                    stroke: ema12.stroke(),
                    windowSize: ema12.options().windowSize,
                  },
                ]}
              />

              <ZoomButtons />
              <OHLCTooltip origin={[8, 16]} textFill={theme.palette.text.primary} />
            </Chart>
            <Chart
              id={4}
              height={elderRayHeight}
              yExtents={[0, elder.accessor()]}
              origin={elderRayOrigin}
              padding={{ top: 8, bottom: 8 }}
            >
              <XAxis showGridLines gridLinesStrokeStyle="#e0e3eb" tickLabelFill={theme.palette.text.primary} strokeStyle={theme.palette.text.primary}/>
              <YAxis ticks={4} tickFormat={pricesDisplayFormat} tickLabelFill={theme.palette.text.primary} strokeStyle={theme.palette.text.primary}/>

              <MouseCoordinateX displayFormat={timeDisplayFormat} />
              <MouseCoordinateY
                rectWidth={margin.right}
                displayFormat={pricesDisplayFormat}
              />

              <ElderRaySeries yAccessor={elder.accessor()} />

              <SingleValueTooltip
                yAccessor={elder.accessor()}
                yLabel="Elder Ray"
                yDisplayFormat={(d) =>
                  `${pricesDisplayFormat(d.bullPower)}, ${pricesDisplayFormat(
                    d.bearPower
                  )}`
                }
                origin={[8, 16]}
              />
            </Chart>
            <CrossHairCursor />
          </ChartCanvas>
        ) : (
          <Skeleton
            variant="rounded"
            width={width}
            height={height}
          />
        )}
      </CardContent>
    </Card>
  );
};

export default function FinanceChart() {
  return <Mainchart />;
}
