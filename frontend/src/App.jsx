import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [stopTimes, setStopTimes] = useState(null);
  const stopId = import.meta.env.VITE_STOP_ID;
  const routeId = import.meta.env.VITE_ROUTE_ID;
  console.log(stopId);
  console.log(routeId);

  useEffect(() => {
    const fetchStopTimes = async () => {
      const response = await fetch(
        `http://localhost:3001/mta/${stopId}/${routeId}`,
      );
      const data = await response.json();
      setStopTimes(data);
    };

    fetchStopTimes();

    const intervalId = setInterval(fetchStopTimes, 60000);
    return () => {
      clearInterval(intervalId);
    };
  }, []);
  return (
    <div className="container">
      <div className="station-line-group">
        <div className="station-title">{stopTimes?.stopName}</div>
      </div>
      <div className="stop-times">{stopTimes?.minutesAway} min</div>
    </div>
  );
}

export default App;
