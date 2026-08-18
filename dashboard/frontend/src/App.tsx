import { useEffect, useState, useCallback, useRef } from 'react';
import { Activity, Zap, Thermometer, Battery, Wifi, WifiOff, RefreshCw, Settings2, Download, Play, Square, AlertTriangle, Clock, ShieldCheck, ActivitySquare, Layers, Flame, TrendingUp, ShieldAlert, CheckCircle2, XCircle, Bug } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Propulsion {
  esc_status: string;
  rpm: number;
  pwm: number;
  thrust: number;
  torque: number;
  power: number;
}

interface Degradation {
  soh: number;
  effective_capacity_ah: number;
  resistance_factor: number;
  equivalent_full_cycles: number;
}

interface ThermalMetrics {
  heat_generation_w: number;
  heat_loss_w: number;
  temp_rate_c_per_s: number;
  ambient_c: number;
}

interface ProtectionStatus {
  over_voltage: boolean;
  under_voltage: boolean;
  over_temperature: boolean;
  under_temperature: boolean;
  over_current: boolean;
  fault: boolean;
  healthy: boolean;
}

interface Telemetry {
  time: string;
  active_profile: string;
  voltage: number;
  current: number;
  soc: number;
  temperature: number;
  endurance_min: number;
  energy_remaining: number;
  cell_voltages?: number[];
  protection_status?: ProtectionStatus;
  thermal_metrics?: ThermalMetrics;
  degradation?: Degradation;
  propulsion?: Propulsion;
}

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [history, setHistory] = useState<Telemetry[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordedData, setRecordedData] = useState<Telemetry[]>([]);
  const recordingRef = useRef(isRecording);

  // Fault injection local state toggles
  const [injectedFaults, setInjectedFaults] = useState({
    over_voltage: false,
    over_temperature: false,
    over_current: false
  });
  
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    recordingRef.current = isRecording;
  }, [isRecording]);

  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/telemetry');
    wsRef.current = ws;
    
    ws.onopen = () => setIsConnected(true);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const now = new Date();
      const timeString = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
      const newData = { ...data, time: timeString };
      
      setTelemetry(newData);
      
      setHistory(prev => {
        const newHistory = [...prev, newData];
        if (newHistory.length > 20) return newHistory.slice(newHistory.length - 20);
        return newHistory;
      });

      if (recordingRef.current) {
        setRecordedData(prev => [...prev, newData]);
      }
    };

    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setIsConnected(false);

    return ws;
  }, []);

  useEffect(() => {
    const ws = connectWebSocket();
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [connectWebSocket]);

  const changeProfile = (profile: string) => {
    setInjectedFaults({ over_voltage: false, over_temperature: false, over_current: false });
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "set_profile", profile }));
    }
  };

  const toggleFault = (faultKey: 'over_voltage' | 'over_temperature' | 'over_current') => {
    const nextState = !injectedFaults[faultKey];
    setInjectedFaults(prev => ({ ...prev, [faultKey]: nextState }));
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "inject_fault", fault: faultKey, state: nextState }));
    }
  };

  const toggleRecording = () => {
    if (!isRecording) {
      setRecordedData([]);
    }
    setIsRecording(!isRecording);
  };

  const exportCSV = () => {
    if (recordedData.length === 0) return;
    
    const headers = ["Time", "Profile", "Voltage (V)", "Current (A)", "SOC (%)", "Temp (C)", "Endurance (min)", "Energy Left (Wh)", "Fault", "SOH (%)", "Cap (Ah)", "R-Factor", "EFC", "RPM", "PWM", "Thrust (kg)", "Torque (Nm)", "Power (W)"];
    const csvRows = [headers.join(",")];
    
    recordedData.forEach(row => {
      csvRows.push([
        row.time,
        row.active_profile,
        row.voltage.toFixed(4),
        row.current.toFixed(4),
        row.soc.toFixed(2),
        row.temperature.toFixed(2),
        row.endurance_min.toFixed(2),
        row.energy_remaining.toFixed(2),
        row.protection_status?.fault ? "FAULTS" : "HEALTHY",
        row.degradation?.soh.toFixed(2) || 100,
        row.degradation?.effective_capacity_ah.toFixed(4) || 0,
        row.degradation?.resistance_factor.toFixed(4) || 1,
        row.degradation?.equivalent_full_cycles.toFixed(4) || 0,
        row.propulsion?.rpm.toFixed(0) || 0,
        row.propulsion?.pwm.toFixed(0) || 0,
        row.propulsion?.thrust.toFixed(4) || 0,
        row.propulsion?.torque.toFixed(4) || 0,
        row.propulsion?.power.toFixed(2) || 0
      ].join(","));
    });
    
    const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', `batterytwin_telemetry_${new Date().getTime()}.csv`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const activeAlerts: string[] = [];
  if (telemetry) {
    if (telemetry.protection_status?.over_voltage) activeAlerts.push("PROTECTION FAULT: Over-Voltage (OV) limit exceeded!");
    if (telemetry.protection_status?.under_voltage) activeAlerts.push("PROTECTION FAULT: Under-Voltage (UV) limit breached!");
    if (telemetry.protection_status?.over_temperature) activeAlerts.push("PROTECTION FAULT: Over-Temperature (OT) limit exceeded!");
    if (telemetry.protection_status?.under_temperature) activeAlerts.push("PROTECTION FAULT: Under-Temperature (UT) limit breached!");
    if (telemetry.protection_status?.over_current) activeAlerts.push("PROTECTION FAULT: Over-Current (OC) limit exceeded!");
    if (telemetry.temperature >= 40) activeAlerts.push("WARNING: High Core Temperature (>40°C). Thermal throttling recommended.");
    if (telemetry.soc <= 20) activeAlerts.push("CRITICAL: Low State of Charge (<20%). Initiate Return-to-Launch (RTL).");
  }

  if (!telemetry && !isConnected) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-300 font-mono">
        Connecting to BatteryTwin Simulation...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 font-sans">
      <header className="mb-8 border-b border-slate-800 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">BatteryTwin Simulator</h1>
          <p className="text-slate-400 mt-1">Dashboard, Validation & Product Engineering</p>
        </div>
        
        <div className="flex items-center gap-4">
          {telemetry?.active_profile && (
            <div className="px-3 py-1.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-mono text-sm">
              Profile: <span className="text-white font-bold">{telemetry.active_profile}</span>
            </div>
          )}

          {isConnected ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border bg-emerald-500/10 border-emerald-500/20 text-emerald-400">
              <Wifi size={16} />
              <span className="text-sm font-medium">Live</span>
            </div>
          ) : (
            <button 
              onClick={connectWebSocket}
              className="flex items-center gap-2 px-3 py-1.5 rounded-full border bg-rose-500/10 border-rose-500/20 text-rose-400 hover:bg-rose-500/20 transition-colors cursor-pointer"
            >
              <WifiOff size={16} />
              <span className="text-sm font-medium">Click to Reconnect</span>
              <RefreshCw size={14} className="ml-1" />
            </button>
          )}
        </div>
      </header>

      {activeAlerts.length > 0 && (
        <div className="mb-8 flex flex-col gap-3 animate-in fade-in slide-in-from-top-4">
          {activeAlerts.map((alert, index) => (
            <div key={index} className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-4 flex items-center gap-3 text-rose-400 font-medium shadow-sm">
              <AlertTriangle size={20} className="animate-pulse" />
              <span>{alert}</span>
            </div>
          ))}
        </div>
      )}

      {/* Control & Fault Injection Panel */}
      <div className="mb-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex items-center gap-4">
          <div className="flex items-center gap-2 text-slate-400 font-medium">
            <Settings2 size={20} />
            <span>Profile:</span>
          </div>
          <div className="flex gap-2">
            <button onClick={() => changeProfile('3S')} className={`px-3 py-2 rounded font-mono text-sm transition-colors border ${telemetry?.active_profile === '3S' ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'}`}>3S</button>
            <button onClick={() => changeProfile('4S')} className={`px-3 py-2 rounded font-mono text-sm transition-colors border ${telemetry?.active_profile === '4S' ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'}`}>4S</button>
            <button onClick={() => changeProfile('6S')} className={`px-3 py-2 rounded font-mono text-sm transition-colors border ${telemetry?.active_profile === '6S' ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'}`}>6S</button>
          </div>
        </div>

        {/* Fault Injection Toggles */}
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex items-center gap-3 lg:col-span-2 flex-wrap">
          <div className="flex items-center gap-2 text-amber-400 font-medium mr-2">
            <Bug size={20} />
            <span>Fault Injection:</span>
          </div>
          <button 
            onClick={() => toggleFault('over_voltage')}
            className={`px-3 py-1.5 rounded font-mono text-xs transition-colors border cursor-pointer ${injectedFaults.over_voltage ? 'bg-rose-600 border-rose-500 text-white font-bold' : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'}`}
          >
            {injectedFaults.over_voltage ? 'OV Fault Active' : 'Inject OV'}
          </button>
          <button 
            onClick={() => toggleFault('over_temperature')}
            className={`px-3 py-1.5 rounded font-mono text-xs transition-colors border cursor-pointer ${injectedFaults.over_temperature ? 'bg-rose-600 border-rose-500 text-white font-bold' : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'}`}
          >
            {injectedFaults.over_temperature ? 'OT Fault Active' : 'Inject OT'}
          </button>
          <button 
            onClick={() => toggleFault('over_current')}
            className={`px-3 py-1.5 rounded font-mono text-xs transition-colors border cursor-pointer ${injectedFaults.over_current ? 'bg-rose-600 border-rose-500 text-white font-bold' : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'}`}
          >
            {injectedFaults.over_current ? 'OC Fault Active' : 'Inject OC'}
          </button>

          <div className="ml-auto flex gap-2">
            <button 
              onClick={toggleRecording}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded font-medium text-xs transition-colors border ${isRecording ? 'bg-red-500/20 border-red-500/50 text-red-400' : 'bg-slate-800 border-slate-700 text-slate-300'}`}
            >
              {isRecording ? <Square size={14} /> : <Play size={14} />}
              {isRecording ? 'Stop' : 'Record'}
            </button>
            <button 
              onClick={exportCSV}
              disabled={recordedData.length === 0 || isRecording}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded font-medium text-xs transition-colors border bg-slate-800 border-slate-700 text-emerald-400 disabled:opacity-50"
            >
              <Download size={14} />
              CSV ({recordedData.length})
            </button>
          </div>
        </div>
      </div>

      {/* Battery Diagnostics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-slate-400 font-medium text-base">Terminal Voltage</h3>
            <Zap className="text-yellow-400" size={22} />
          </div>
          <p className="text-4xl font-mono text-slate-100">{telemetry?.voltage.toFixed(2) || '0.00'} <span className="text-xl text-slate-500">V</span></p>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-slate-400 font-medium text-base">Load Current</h3>
            <Activity className="text-blue-400" size={22} />
          </div>
          <p className="text-4xl font-mono text-slate-100">{telemetry?.current.toFixed(2) || '0.00'} <span className="text-xl text-slate-500">A</span></p>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-slate-400 font-medium text-base">State of Charge</h3>
            <Battery className="text-green-400" size={22} />
          </div>
          <p className="text-4xl font-mono text-slate-100">{telemetry?.soc.toFixed(1) || '0.0'} <span className="text-xl text-slate-500">%</span></p>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-slate-400 font-medium text-base">Core Temp</h3>
            <Thermometer className={telemetry && telemetry.temperature >= 40 ? "text-rose-500 animate-pulse" : "text-red-400"} size={22} />
          </div>
          <p className={`text-4xl font-mono ${telemetry && telemetry.temperature >= 40 ? "text-rose-500" : "text-slate-100"}`}>{telemetry?.temperature.toFixed(1) || '0.0'} <span className="text-xl text-slate-500">°C</span></p>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg border-indigo-500/30">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-indigo-400 font-medium text-base">Flight Endurance</h3>
            <Clock className="text-indigo-400" size={22} />
          </div>
          <p className="text-4xl font-mono text-slate-100">{telemetry?.endurance_min.toFixed(1) || '0.0'} <span className="text-xl text-slate-500">min</span></p>
        </div>
      </div>

      {/* Protection & Safety Interlocks Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <div className={`p-4 rounded-xl border shadow-lg flex flex-col justify-between ${telemetry?.protection_status?.over_voltage ? 'bg-rose-500/10 border-rose-500/50 text-rose-400' : 'bg-slate-900 border-slate-700 text-slate-300'}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Over-Voltage (OV)</span>
            {telemetry?.protection_status?.over_voltage ? <XCircle size={18} className="text-rose-400" /> : <CheckCircle2 size={18} className="text-emerald-400" />}
          </div>
          <p className="text-xl font-mono font-bold">{telemetry?.protection_status?.over_voltage ? 'FAULT' : 'NORMAL'}</p>
        </div>
        
        <div className={`p-4 rounded-xl border shadow-lg flex flex-col justify-between ${telemetry?.protection_status?.under_voltage ? 'bg-rose-500/10 border-rose-500/50 text-rose-400' : 'bg-slate-900 border-slate-700 text-slate-300'}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Under-Voltage (UV)</span>
            {telemetry?.protection_status?.under_voltage ? <XCircle size={18} className="text-rose-400" /> : <CheckCircle2 size={18} className="text-emerald-400" />}
          </div>
          <p className="text-xl font-mono font-bold">{telemetry?.protection_status?.under_voltage ? 'FAULT' : 'NORMAL'}</p>
        </div>

        <div className={`p-4 rounded-xl border shadow-lg flex flex-col justify-between ${telemetry?.protection_status?.over_temperature ? 'bg-rose-500/10 border-rose-500/50 text-rose-400' : 'bg-slate-900 border-slate-700 text-slate-300'}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Over-Temp (OT)</span>
            {telemetry?.protection_status?.over_temperature ? <XCircle size={18} className="text-rose-400" /> : <CheckCircle2 size={18} className="text-emerald-400" />}
          </div>
          <p className="text-xl font-mono font-bold">{telemetry?.protection_status?.over_temperature ? 'FAULT' : 'NORMAL'}</p>
        </div>

        <div className={`p-4 rounded-xl border shadow-lg flex flex-col justify-between ${telemetry?.protection_status?.under_temperature ? 'bg-rose-500/10 border-rose-500/50 text-rose-400' : 'bg-slate-900 border-slate-700 text-slate-300'}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Under-Temp (UT)</span>
            {telemetry?.protection_status?.under_temperature ? <XCircle size={18} className="text-rose-400" /> : <CheckCircle2 size={18} className="text-emerald-400" />}
          </div>
          <p className="text-xl font-mono font-bold">{telemetry?.protection_status?.under_temperature ? 'FAULT' : 'NORMAL'}</p>
        </div>

        <div className={`p-4 rounded-xl border shadow-lg flex flex-col justify-between ${telemetry?.protection_status?.over_current ? 'bg-rose-500/10 border-rose-500/50 text-rose-400' : 'bg-slate-900 border-slate-700 text-slate-300'}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Over-Current (OC)</span>
            {telemetry?.protection_status?.over_current ? <XCircle size={18} className="text-rose-400" /> : <CheckCircle2 size={18} className="text-emerald-400" />}
          </div>
          <p className="text-xl font-mono font-bold">{telemetry?.protection_status?.over_current ? 'FAULT' : 'NORMAL'}</p>
        </div>

        <div className={`p-4 rounded-xl border shadow-lg flex flex-col justify-between ${telemetry?.protection_status?.healthy ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-400' : 'bg-rose-500/10 border-rose-500/50 text-rose-400'}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Protection Interlock</span>
            <ShieldAlert size={18} />
          </div>
          <p className="text-xl font-mono font-bold">{telemetry?.protection_status?.healthy ? 'ARMED / SAFE' : 'TRIPPED'}</p>
        </div>
      </div>

      {/* Thermal Fault & Dissipation Analytics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-orange-400 font-medium text-sm">Joule Heat Generation</h3>
            <Flame className="text-orange-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.thermal_metrics?.heat_generation_w.toFixed(2) || '0.00'} <span className="text-lg text-slate-500">W</span></p>
        </div>
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-blue-400 font-medium text-sm">Convective Heat Loss</h3>
            <ActivitySquare className="text-blue-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.thermal_metrics?.heat_loss_w.toFixed(2) || '0.00'} <span className="text-lg text-slate-500">W</span></p>
        </div>
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-amber-400 font-medium text-sm">Temperature Rate</h3>
            <TrendingUp className="text-amber-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.thermal_metrics?.temp_rate_c_per_s.toFixed(4) || '0.0000'} <span className="text-lg text-slate-500">°C/s</span></p>
        </div>
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-cyan-400 font-medium text-sm">Ambient Reference</h3>
            <Thermometer className="text-cyan-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.thermal_metrics?.ambient_c.toFixed(1) || '25.0'} <span className="text-lg text-slate-500">°C</span></p>
        </div>
      </div>

      {/* SOH & Aging Analytics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-emerald-400 font-medium text-sm">State of Health (SOH)</h3>
            <ShieldCheck className="text-emerald-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.degradation?.soh.toFixed(2) || '100.00'} <span className="text-lg text-slate-500">%</span></p>
        </div>
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-slate-400 font-medium text-sm">Effective Capacity</h3>
            <Battery className="text-teal-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.degradation?.effective_capacity_ah.toFixed(3) || '0.000'} <span className="text-lg text-slate-500">Ah</span></p>
        </div>
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-slate-400 font-medium text-sm">Resistance Multiplier</h3>
            <ActivitySquare className="text-amber-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.degradation?.resistance_factor.toFixed(3) || '1.000'} <span className="text-lg text-slate-500">x</span></p>
        </div>
        <div className="bg-slate-900 p-5 rounded-xl border border-slate-700 shadow-lg">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-slate-400 font-medium text-sm">Equivalent Full Cycles</h3>
            <RefreshCw className="text-cyan-400" size={20} />
          </div>
          <p className="text-3xl font-mono text-slate-100">{telemetry?.degradation?.equivalent_full_cycles.toFixed(3) || '0.000'} <span className="text-lg text-slate-500">EFC</span></p>
        </div>
      </div>

      {/* Cell-Level Voltage Distribution & Balancing View */}
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg mb-8">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <Layers className="text-indigo-400" size={20} />
            <h3 className="text-slate-200 font-medium text-lg">Cell-Level Voltage Distribution ({telemetry?.active_profile || '6S'} Pack)</h3>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">Balanced Active</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {telemetry?.cell_voltages?.map((cellVolt, index) => (
            <div key={index} className="bg-slate-950 p-4 rounded-lg border border-slate-800 flex flex-col justify-between">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-slate-400 font-medium">Cell {index + 1}</span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              </div>
              <p className="text-2xl font-mono text-slate-100">{cellVolt.toFixed(3)} <span className="text-xs text-slate-500">V</span></p>
            </div>
          ))}
        </div>
      </div>

      {/* Battery Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg">
          <h3 className="text-slate-400 font-medium text-lg mb-4">Voltage Discharge Curve (V)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="voltage" stroke="#facc15" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-lg">
          <h3 className="text-slate-400 font-medium text-lg mb-4">Dynamic Load (A)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                <YAxis domain={['auto', 'auto']} stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="current" stroke="#60a5fa" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Powertrain Dashboard */}
      <h2 className="text-xl font-semibold text-slate-200 mb-4 pt-4 border-t border-slate-800">Powertrain Analysis</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex flex-col justify-between">
          <p className="text-slate-400 text-sm font-medium mb-2">ESC Status</p>
          <p className="text-2xl font-mono text-emerald-400">{telemetry?.propulsion?.esc_status || 'WAIT'}</p>
        </div>
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex flex-col justify-between">
          <p className="text-slate-400 text-sm font-medium mb-2">Motor RPM</p>
          <p className="text-2xl font-mono text-slate-100">{telemetry?.propulsion?.rpm.toFixed(0) || '0'}</p>
        </div>
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex flex-col justify-between">
          <p className="text-slate-400 text-sm font-medium mb-2">PWM Signal</p>
          <p className="text-2xl font-mono text-slate-100">{telemetry?.propulsion?.pwm.toFixed(0) || '0'} <span className="text-xs text-slate-500">μs</span></p>
        </div>
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex flex-col justify-between">
          <p className="text-slate-400 text-sm font-medium mb-2">Thrust</p>
          <p className="text-2xl font-mono text-slate-100">{telemetry?.propulsion?.thrust.toFixed(2) || '0.00'} <span className="text-xs text-slate-500">kg</span></p>
        </div>
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex flex-col justify-between">
          <p className="text-slate-400 text-sm font-medium mb-2">Torque</p>
          <p className="text-2xl font-mono text-slate-100">{telemetry?.propulsion?.torque.toFixed(2) || '0.00'} <span className="text-xs text-slate-500">Nm</span></p>
        </div>
        <div className="bg-slate-900 p-4 rounded-xl border border-slate-700 shadow-sm flex flex-col justify-between">
          <p className="text-slate-400 text-sm font-medium mb-2">Power Cons.</p>
          <p className="text-2xl font-mono text-slate-100">{telemetry?.propulsion?.power.toFixed(0) || '0'} <span className="text-xs text-slate-500">W</span></p>
        </div>
      </div>
    </div>
  );
}
