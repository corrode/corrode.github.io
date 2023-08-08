"use strict";

// Check if the host is localhost or 127.0.0.1
if (
  window.location.hostname !== "localhost" &&
  window.location.hostname !== "127.0.0.1"
) {
  const oxitraffic_base_url = "https://oxitraffic-corrode-dev.mo8it.com";
  const sleep_in_seconds = 20;

  // Register and get an ID.
  const registration_response = await fetch(
    oxitraffic_base_url + "/register?path=" + window.location.pathname
  );
  const registration_id = await registration_response.json();

  // Sleep the required amount before being able to call `/post-sleep`.
  await new Promise((resolve) =>
    setTimeout(() => resolve(), sleep_in_seconds * 1000)
  );

  // Call `/post-sleep` for the visit to be counted.
  await fetch(oxitraffic_base_url + "/post-sleep/" + registration_id);
}
