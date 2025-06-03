import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Box, Grid, Slider, Typography, Paper, Button, CircularProgress } from '@mui/material';

export default function LedControlDashboard() {
  const [r, setR] = useState(0);
  const [g, setG] = useState(0);
  const [b, setB] = useState(0);
  const [brightness, setBrightness] = useState(65);
  const [memoryUsage, setMemoryUsage] = useState({ used: 0, total: 0, percent: 0 });
  const [sdUsage, setSdUsage] = useState({ used: 0, total: 0, percent: 0 });
  const [imageSrc, setImageSrc] = useState('');
  const [lastUpload, setLastUpload] = useState('');
  const [backupRunning, setBackupRunning] = useState(false);
  const [backupStatus, setBackupStatus] = useState({});
  const [ledInitialized, setLedInitialized] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [cpuTemp, setCpuTemp] = useState(null);


   // Met à jour l'heure toutes les secondes
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) =>
    date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });


  const fetchStats = async () => {
    const res = await axios.get('/api/stats');
    setMemoryUsage(res.data.memory);
    setSdUsage(res.data.sd);
    if (res.data.cpu) {
      setCpuTemp(res.data.cpu.temperature_celsius);
    }
  };

  const fetchImage = async () => {
    const timestamp = Date.now();
    setImageSrc(`/images/usb_cam_0/latest.jpg?t=${timestamp}`);
  };

  const applySettings = async (rVal, gVal, bVal, brightnessVal) => {
    await axios.post('/api/set-leds', { r: rVal, g: gVal, b: bVal, brightness: brightnessVal });
  };

  const triggerBackup = async () => {
    await axios.post('/api/manual-backup');
    fetchBackupStatus();
  };

  const fetchBackupStatus = async () => {
    const res = await axios.get('/api/backup-status');
    setBackupStatus(res.data);
    setBackupRunning(res.data.running);
  };

  const fetchLastUpload = async () => {
    const res = await axios.get('/api/last-upload');
    setLastUpload(res.data.last);
  };

  const fetchLedState = async () => {
    try {
      const res = await axios.get('/api/led-state');
      setR(res.data.r);
      setG(res.data.g);
      setB(res.data.b);
      setBrightness(res.data.brightness);
      setLedInitialized(true);
    } catch (err) {
      console.error('Erreur lors de la récupération de l\'état des LEDs:', err);
    }
  };

  useEffect(() => {
    fetchLedState();
    fetchLastUpload();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchStats();
      fetchImage();
      fetchBackupStatus();
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (ledInitialized) {
      applySettings(r, g, b, brightness);
    }
  }, [r, g, b, brightness, ledInitialized]);

  return (
    <Box sx={{ p: 4, background: 'linear-gradient(to bottom right, #e6f0fa, #fef2f8, #fff8e7)', minHeight: '100vh' }}>
      <Box maxWidth="lg" mx="auto" sx={{ position: 'relative' }}>
        {/* Heure en haut à droite */}
        <Box sx={{ position: 'absolute', top: 0, right: 0, p: 2 }}>
          <Typography variant="subtitle1" color="textSecondary">
            {formatTime(currentTime)}
          </Typography>
        </Box>

        <Typography variant="h4" align="center" gutterBottom>
          LED Strip Controller + Camera Live View
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" color="primary" gutterBottom>
                Contrôle des LEDs
              </Typography>

              <Typography gutterBottom>Rouge</Typography>
              <Slider value={r} min={0} max={255} onChange={(e, val) => setR(val)} />

              <Typography gutterBottom>Vert</Typography>
              <Slider value={g} min={0} max={255} onChange={(e, val) => setG(val)} />

              <Typography gutterBottom>Bleu</Typography>
              <Slider value={b} min={0} max={255} onChange={(e, val) => setB(val)} />

              <Typography gutterBottom>Intensité</Typography>
              <Slider value={brightness} min={0} max={255} onChange={(e, val) => setBrightness(val)} />
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" color="primary" gutterBottom>
                État du système
              </Typography>

              <Typography variant="subtitle1" color="secondary">Mémoire</Typography>
              <Typography>Utilisée: {memoryUsage.used} MB</Typography>
              <Typography>Totale: {memoryUsage.total} MB</Typography>
              <Typography>Utilisation: {memoryUsage.percent}%</Typography>

              <Box mt={2}>
                <Typography variant="subtitle1" color="secondary">Carte SD</Typography>
                <Typography>Utilisée: {sdUsage.used} MB</Typography>
                <Typography>Totale: {sdUsage.total} MB</Typography>
                <Typography>Utilisation: {sdUsage.percent}%</Typography>
              </Box>
              <Box mt={2}>
                <Typography variant="subtitle1" color="secondary">Température CPU</Typography>
                <Typography>{cpuTemp !== null ? `${cpuTemp} °C` : 'N/A'}</Typography>
              </Box>

            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" color="primary" gutterBottom>
                Sauvegarde
              </Typography>

              <Typography variant="subtitle1" color="secondary">Dernière sauvegarde</Typography>
              <Typography>{lastUpload}</Typography>

              <Box mt={2}>
                <Button variant="contained" disabled={backupRunning} onClick={triggerBackup}>
                  {backupRunning ? 'Sauvegarde en cours...' : 'Forcer l\'envoi'}
                </Button>
                {backupRunning && <Box mt={2}><CircularProgress size={24} /></Box>}
              </Box>

              <Box mt={2}>
                <Typography variant="subtitle2">Statut :</Typography>
                <Typography color={backupRunning ? 'orange' : 'green'}>
                  {backupRunning ? 'En cours' : 'Repos'}
                </Typography>

                {backupStatus.start_time && (
                  <Typography variant="body2">Démarré à : {backupStatus.start_time}</Typography>
                )}
                {backupStatus.end_time && (
                  <Typography variant="body2">Terminé à : {backupStatus.end_time}</Typography>
                )}
                {backupStatus.log && (
                  <Typography variant="caption" display="block" sx={{ whiteSpace: 'pre-wrap' }}>
                    {backupStatus.log}
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>

        <Box mt={4} textAlign="center">
          <Typography variant="h6" color="primary" gutterBottom>
            Dernière image de la caméra
          </Typography>
          {imageSrc ? (
            <img
              src={imageSrc}
              alt="Dernière image"
              onError={() => setImageSrc('')}
              style={{ maxWidth: '100%', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
            />
          ) : (
            <Typography variant="body2" color="textSecondary">Aucune image disponible pour le moment.</Typography>
          )}
        </Box>
      </Box>
    </Box>
  );
}