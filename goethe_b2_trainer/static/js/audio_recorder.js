/**
 * Audio Recorder with Live Waveform Visualizer for Goethe B2 Sprechen Module.
 */

class GoetheAudioRecorder {
  constructor(options = {}) {
    this.canvasId = options.canvasId || 'waveformCanvas';
    this.timerId = options.timerId || 'recTimerDisplay';
    this.previewAudioId = options.previewAudioId || 'audioPlaybackPreview';
    
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.audioBlob = null;
    this.audioBase64 = null;
    this.stream = null;
    this.audioContext = null;
    this.analyser = null;
    this.source = null;
    this.animationId = null;
    
    this.isRecording = false;
    this.startTime = null;
    this.timerInterval = null;
    this.durationSeconds = 0;
  }

  async checkPermission() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Release stream immediately after check
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (e) {
      console.warn('Microphone access denied or unavailable:', e);
      return false;
    }
  }

  async start() {
    if (this.isRecording) return;
    
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
    } catch (err) {
      alert('Mikrofonzugriff fehlgeschlagen: ' + err.message);
      throw err;
    }

    // Set up Web Audio API Analyser for live visualizer
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    this.audioContext = new AudioContextClass();
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 256;
    this.source = this.audioContext.createMediaStreamSource(this.stream);
    this.source.connect(this.analyser);

    // Set up MediaRecorder
    let mimeType = 'audio/webm;codecs=opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      if (MediaRecorder.isTypeSupported('audio/webm')) mimeType = 'audio/webm';
      else if (MediaRecorder.isTypeSupported('audio/mp4')) mimeType = 'audio/mp4';
      else mimeType = ''; // Let browser choose default
    }

    this.audioChunks = [];
    this.mediaRecorder = mimeType ? new MediaRecorder(this.stream, { mimeType }) : new MediaRecorder(this.stream);
    
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.audioChunks.push(event.data);
      }
    };

    this.mediaRecorder.start(250); // collect 250ms chunks
    this.isRecording = true;
    this.startTime = Date.now();
    this.durationSeconds = 0;

    // Start timer display
    this._startTimer();

    // Start live canvas visualization
    this._startVisualizer();
  }

  async stop() {
    if (!this.isRecording || !this.mediaRecorder) return null;

    return new Promise((resolve) => {
      this.mediaRecorder.onstop = async () => {
        this.isRecording = false;
        clearInterval(this.timerInterval);
        cancelAnimationFrame(this.animationId);

        // Stop all mic tracks
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext && this.audioContext.state !== 'closed') {
          try { await this.audioContext.close(); } catch (_) {}
        }

        const mime = this.mediaRecorder.mimeType || 'audio/webm';
        this.audioBlob = new Blob(this.audioChunks, { type: mime });
        this.audioBase64 = await this._blobToBase64(this.audioBlob);

        // Update preview audio element
        const preview = document.getElementById(this.previewAudioId);
        if (preview) {
          preview.src = URL.createObjectURL(this.audioBlob);
          preview.style.display = 'block';
        }

        this._drawIdleVisualizer();

        resolve({
          blob: this.audioBlob,
          base64: this.audioBase64,
          mimeType: mime,
          durationSeconds: this.durationSeconds,
        });
      };

      this.mediaRecorder.stop();
    });
  }

  _startTimer() {
    const timerElem = document.getElementById(this.timerId);
    if (!timerElem) return;

    this.timerInterval = setInterval(() => {
      this.durationSeconds = Math.floor((Date.now() - this.startTime) / 1000);
      const mins = String(Math.floor(this.durationSeconds / 60)).padStart(2, '0');
      const secs = String(this.durationSeconds % 60).padStart(2, '0');
      timerElem.textContent = `${mins}:${secs}`;
    }, 500);
  }

  _startVisualizer() {
    const canvas = document.getElementById(this.canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      this.animationId = requestAnimationFrame(draw);
      this.analyser.getByteFrequencyData(dataArray);

      ctx.fillStyle = '#0a0d14';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.2;
      let barHeight;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        barHeight = (dataArray[i] / 255) * canvas.height * 0.9;

        // Gradient color from blue to cyan
        const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
        gradient.addColorStop(0, '#06b6d4');
        gradient.addColorStop(1, '#2563eb');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
        x += barWidth;
      }
    };

    draw();
  }

  _drawIdleVisualizer() {
    const canvas = document.getElementById(this.canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#0a0d14';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw a calm center resting line
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
  }

  _blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result;
        // Strip the data URL prefix (e.g. data:audio/webm;base64,)
        const base64 = dataUrl.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }
}
