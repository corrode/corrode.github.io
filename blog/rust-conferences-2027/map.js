(() => {
  const container = document.getElementById('conference-map');
  if (!container || typeof L === 'undefined') return;

  // City coordinates, not venue locations. Unconfirmed editions are omitted.
  const conferences = [
    { name: 'Rust Nation UK', city: 'London, UK', coordinates: [51.5074, -0.1278], dates: 'February 18, 2027' },
    { name: 'TokioConf', city: 'Portland, USA', coordinates: [45.5152, -122.6784], dates: 'April 26-27, 2027' },
    { name: 'RustWeek', city: 'Utrecht, Netherlands', coordinates: [52.0907, 5.1214], dates: 'May 24-29, 2027' },
    { name: 'RustConf', city: 'Vancouver, Canada + Online', coordinates: [49.2827, -123.1207], dates: 'September 7-10, 2027' },
    { name: 'Oxidize', city: 'Berlin, Germany', coordinates: [52.5200, 13.4050], dates: 'September 14-16, 2027' },
    { name: 'EuroRust', city: 'Prague, Czech Republic + Online', coordinates: [50.0755, 14.4378], dates: 'October 13-16, 2027 (talks October 14-15)' },
    { name: 'FOSDEM Rust Devroom', city: 'Brussels, Belgium', coordinates: [50.8503, 4.3517], dates: 'January 31, 2027' },
    { name: 'Rust Verification Workshop', city: 'Copenhagen, Denmark', coordinates: [55.6761, 12.5683], dates: '2027 — dates to be announced' },
    { name: 'PLRust', city: 'Kyoto, Japan', coordinates: [35.0116, 135.7681], dates: 'March 15, 2027' }
  ];

  container.hidden = false;
  const map = L.map(container, {
    scrollWheelZoom: false,
    maxZoom: 10
  });

  const tileOptions = {
    maxZoom: 20,
    attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> &copy; <a href="https://stamen.com/">Stamen Design</a> &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  };
  // Stadia supports domain authentication on corrode.dev and localhost access.
  const lightLayer = L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png', tileOptions);
  const darkLayer = L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}{r}.png', tileOptions);
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');

  function updateMapTheme() {
    const scheme = typeof getPreferredColorScheme === 'function'
      ? getPreferredColorScheme()
      : (systemTheme.matches ? 'dark' : 'light');
    const active = scheme === 'dark' ? darkLayer : lightLayer;
    const inactive = scheme === 'dark' ? lightLayer : darkLayer;
    if (map.hasLayer(inactive)) map.removeLayer(inactive);
    if (!map.hasLayer(active)) active.addTo(map);
  }

  updateMapTheme();
  document.getElementById('theme-toggle')?.addEventListener('click', updateMapTheme);
  systemTheme.addEventListener('change', updateMapTheme);

  conferences.forEach(conference => {
    const content = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = conference.name;
    content.append(title);
    [conference.dates, conference.city].forEach(text => {
      const line = document.createElement('div');
      line.textContent = text;
      content.append(line);
    });

    L.marker(conference.coordinates, {
      title: conference.name,
      alt: conference.name,
      icon: L.divIcon({
        className: 'conference-marker',
        html: '<span></span>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      })
    }).addTo(map).bindTooltip(content).bindPopup(content.cloneNode(true));
  });

  const bounds = L.latLngBounds(conferences.map(conference => conference.coordinates));
  map.fitBounds(bounds, { padding: [30, 30], maxZoom: 3 });
})();
