import { routeMap } from "./config.js";
import stops from "./data/stops.json" with { type: "json" };
import "dotenv/config";
import express from "express";
import GtfsRealtimeBindings from "gtfs-realtime-bindings";
import cors from "cors";
const app = express();
const port = process.env.PORT;

const cache = {
  feed: null,
  timestamp: 0,
  feedUrl: null,
};

const getFeed = async (apiUrl) => {
  if (cache.feedUrl === apiUrl && Date.now() - cache.timestamp < 30000) {
    feed = cache.feed;
  } else {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error("Failed response.");
    }
    const buffer = await response.arrayBuffer();
    feed = GtfsRealtimeBindings.transit_realtime.FeedMessage.decode(
      new Uint8Array(buffer),
    );
    cache.feed = feed;
    cache.timestamp = Date.now();
    cache.feedUrl = apiUrl;
  }
  return feed;
};

app.use(cors());

app.get("/", (req, res) => {
  res.send("MTA");
});

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.get("/mta/:stopId/:routeId", async (req, res) => {
  const { stopId, routeId } = req.params;
  if (!stops[stopId]) {
    return res.status(400).json({ error: "invalid stop id" });
  }
  if (!routeMap[routeId]) {
    return res.status(400).json({ error: "invalid route id" });
  }
  const apiUrl = routeMap[routeId];

  try {
    const stopName = stops[stopId].stop_name;
    const feed = await getFeed(apiUrl);
    const stopTimes = [];
    const now = Date.now() / 1000;
    feed.entity.forEach((entity) => {
      if (entity.tripUpdate?.trip?.routeId === routeId) {
        const stopTime = entity.tripUpdate.stopTimeUpdate;
        stopTime.forEach((s) => {
          if (s.stopId === stopId) {
            const arrivalTime = s.arrival?.time?.low;
            const minutesAway = Math.max(
              Math.floor((arrivalTime - now) / 60),
              0,
            );
            stopTimes.push({ routeId, stopName, arrivalTime, minutesAway });
          }
        });
      }
    });
    stopTimes.sort((a, b) => a.minutesAway - b.minutesAway);
    if (stopTimes.length === 0) {
      return res.status(404).json({
        routeId,
        stopName,
        arrivalTime: null,
        minutesAway: null,
      });
    }
    res.json(stopTimes[0]);
  } catch (error) {
    res.status(500).json({ error: "failed to fetch MTA data" });
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
