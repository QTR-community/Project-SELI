from django.test import TestCase

# Create your tests here.
'''
<button id="triggerLight">⚡ There’s Light</button>
<div id="status"></div>

<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
  const socket = io("http://127.0.0.1:5000");

  document.getElementById("triggerLight").addEventListener("click", () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        socket.emit("trigger_survey", {
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          user_id: "123"
        });
      });
    }
  });

  socket.on("survey_prompt", (data) => {
    const confirmLight = confirm(`Is there light at ${data.street}, ${data.city}?`);
    socket.emit("survey_response", {
      survey_id: data.survey_id,
      user_id: "123",
      response: confirmLight
    });
  });

  socket.on("survey_update", (data) => {
    document.getElementById("status").innerText =
      `Street: ${data.street}, Probability: ${data.probability}% (${data.status})`;
  });
</script>

'''