function startListening() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.start();

  recognition.onresult = function (event) {
    const command = event.results[0][0].transcript;
    document.getElementById('commandText').innerText = `You said: "${command}"`;

    // First: send the voice command to the backend
    fetch('/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command })
    })
    .then(res => res.json())
    .then(async (data) => {
      document.getElementById('responseText').innerText = data.reply || '';

      if (data.image) {
        const img = document.getElementById('responseImage');
        img.src = data.image;
        img.style.display = 'block';
      } else {
        document.getElementById('responseImage').style.display = 'none';
      }

      // Second: request the audio directly from backend (no file saving)
      if (data.reply) {
        const audioRes = await fetch('/speak', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: data.reply })
        });

        if (audioRes.ok) {
          const blob = await audioRes.blob();
          const url = URL.createObjectURL(blob);
          const audio = new Audio(url);
          audio.play();
          audio.onended = () => URL.revokeObjectURL(url); // Clean up
        } else {
          console.error("Failed to fetch audio");
        }
      }
    })
    .catch(err => console.error("Error:", err));
  };
}
