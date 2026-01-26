import "dotenv/config";
const apiUrl = process.env.MTA_API_URL;

export const feedMap = {
  "nyct%2Fgtfs-bdfm": ["B", "D", "F", "M"],
  "nyct%2Fgtfs-ace": ["A", "C", "E"],
  "nyct%2Fgtfs-g": ["G"],
  "nyct%2Fgtfs-jz": ["J", "Z"],
  "nyct%2Fgtfs-nqrw": ["N", "Q", "R", "W"],
  "nyct%2Fgtfs-l": ["L"],
  "nyct%2Fgtfs": ["1", "2", "3", "4", "5", "6", "7", "S"],
};

export const routeMap = {};
Object.entries(feedMap).forEach(([feed, routes]) => {
  routes.forEach((route) => {
    routeMap[route] = `${apiUrl}/${feed}`;
  });
});
