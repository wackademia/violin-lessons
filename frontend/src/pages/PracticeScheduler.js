import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Clock, Calendar as CalIcon } from 'lucide-react';
import { api } from '../utils/api';

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const FOCUS_AREAS = ['General Practice', 'Scales & Arpeggios', 'Etudes', 'Repertoire', 'Sight Reading', 'Music Theory', 'Bowing Technique'];

export default function PracticeScheduler() {
  const [schedule, setSchedule] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddSchedule, setShowAddSchedule] = useState(false);
  const [showAddLog, setShowAddLog] = useState(false);
  const [newSchedule, setNewSchedule] = useState({ day_of_week: 1, time: '18:00', duration_minutes: 30, focus_area: 'General Practice' });
  const [newLog, setNewLog] = useState({ date: new Date().toISOString().split('T')[0], duration_minutes: 30, notes: '' });

  useEffect(() => {
    Promise.all([api.getSchedule(), api.getPracticeLogs()])
      .then(([s, l]) => { setSchedule(s); setLogs(l); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const addScheduleEntry = async () => {
    const entry = await api.createSchedule(newSchedule);
    setSchedule([...schedule, entry]);
    setShowAddSchedule(false);
    setNewSchedule({ day_of_week: 1, time: '18:00', duration_minutes: 30, focus_area: 'General Practice' });
  };

  const removeScheduleEntry = async (id) => {
    await api.deleteSchedule(id);
    setSchedule(schedule.filter(s => s.id !== id));
  };

  const addPracticeLog = async () => {
    const log = await api.createPracticeLog(newLog);
    setLogs([log, ...logs]);
    setShowAddLog(false);
    setNewLog({ date: new Date().toISOString().split('T')[0], duration_minutes: 30, notes: '' });
  };

  const removeLog = async (id) => {
    await api.deletePracticeLog(id);
    setLogs(logs.filter(l => l.id !== id));
  };

  const totalMinutes = logs.reduce((sum, l) => sum + l.duration_minutes, 0);

  return (
    <div className="space-y-8" data-testid="practice-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-stone-100">Practice Scheduler</h1>
        <p className="text-stone-400 font-body text-sm mt-2">Plan and track your practice sessions</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="p-4 rounded-2xl bg-background-secondary border border-stone-800" data-testid="total-sessions">
          <p className="text-stone-500 text-xs font-body">Total Sessions</p>
          <p className="font-heading text-2xl font-bold text-stone-100 mt-1">{logs.length}</p>
        </div>
        <div className="p-4 rounded-2xl bg-background-secondary border border-stone-800" data-testid="total-minutes">
          <p className="text-stone-500 text-xs font-body">Total Minutes</p>
          <p className="font-heading text-2xl font-bold text-stone-100 mt-1">{totalMinutes}</p>
        </div>
        <div className="p-4 rounded-2xl bg-background-secondary border border-stone-800 col-span-2 md:col-span-1" data-testid="weekly-schedule-count">
          <p className="text-stone-500 text-xs font-body">Weekly Schedule</p>
          <p className="font-heading text-2xl font-bold text-stone-100 mt-1">{schedule.length} days</p>
        </div>
      </div>

      {/* Weekly Schedule */}
      <section data-testid="weekly-schedule-section">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-xl font-bold text-stone-100">Weekly Schedule</h2>
          <button
            onClick={() => setShowAddSchedule(!showAddSchedule)}
            data-testid="add-schedule-btn"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-primary text-white font-body font-medium text-xs hover:bg-primary-hover transition-all"
          >
            <Plus size={14} /> Add Day
          </button>
        </div>

        {showAddSchedule && (
          <div className="p-4 rounded-2xl bg-background-secondary border border-stone-800 mb-4 space-y-3" data-testid="add-schedule-form">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-stone-500 text-xs font-body block mb-1">Day</label>
                <select
                  value={newSchedule.day_of_week}
                  onChange={(e) => setNewSchedule({...newSchedule, day_of_week: Number(e.target.value)})}
                  data-testid="schedule-day-select"
                  className="w-full px-3 py-2 rounded-xl bg-stone-800 border border-stone-700 text-stone-200 font-body text-sm focus:outline-none focus:border-primary/50"
                >
                  {DAYS.map((d, i) => <option key={i} value={i}>{d}</option>)}
                </select>
              </div>
              <div>
                <label className="text-stone-500 text-xs font-body block mb-1">Time</label>
                <input
                  type="time"
                  value={newSchedule.time}
                  onChange={(e) => setNewSchedule({...newSchedule, time: e.target.value})}
                  data-testid="schedule-time-input"
                  className="w-full px-3 py-2 rounded-xl bg-stone-800 border border-stone-700 text-stone-200 font-body text-sm focus:outline-none focus:border-primary/50"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-stone-500 text-xs font-body block mb-1">Duration (min)</label>
                <input
                  type="number"
                  value={newSchedule.duration_minutes}
                  onChange={(e) => setNewSchedule({...newSchedule, duration_minutes: Number(e.target.value)})}
                  data-testid="schedule-duration-input"
                  className="w-full px-3 py-2 rounded-xl bg-stone-800 border border-stone-700 text-stone-200 font-body text-sm focus:outline-none focus:border-primary/50"
                />
              </div>
              <div>
                <label className="text-stone-500 text-xs font-body block mb-1">Focus Area</label>
                <select
                  value={newSchedule.focus_area}
                  onChange={(e) => setNewSchedule({...newSchedule, focus_area: e.target.value})}
                  data-testid="schedule-focus-select"
                  className="w-full px-3 py-2 rounded-xl bg-stone-800 border border-stone-700 text-stone-200 font-body text-sm focus:outline-none focus:border-primary/50"
                >
                  {FOCUS_AREAS.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>
            </div>
            <button
              onClick={addScheduleEntry}
              data-testid="save-schedule-btn"
              className="w-full py-2.5 rounded-xl bg-primary text-white font-body font-medium text-sm hover:bg-primary-hover transition-all"
            >
              Save
            </button>
          </div>
        )}

        {schedule.length > 0 ? (
          <div className="space-y-2">
            {schedule.sort((a, b) => a.day_of_week - b.day_of_week).map((entry) => (
              <div key={entry.id} className="flex items-center justify-between p-4 rounded-xl bg-background-secondary border border-stone-800" data-testid={`schedule-entry-${entry.id}`}>
                <div className="flex items-center gap-3">
                  <CalIcon size={16} className="text-cyan-400" />
                  <div>
                    <p className="font-body font-medium text-stone-200 text-sm">{DAYS[entry.day_of_week]} at {entry.time}</p>
                    <p className="text-stone-500 text-xs">{entry.duration_minutes} min &middot; {entry.focus_area}</p>
                  </div>
                </div>
                <button onClick={() => removeScheduleEntry(entry.id)} data-testid={`delete-schedule-${entry.id}`} className="p-2 text-stone-600 hover:text-red-400 transition-colors">
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-stone-600 text-sm font-body py-4">No schedule set. Add your practice days above.</p>
        )}
      </section>

      {/* Practice Log */}
      <section data-testid="practice-log-section">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-xl font-bold text-stone-100">Practice Log</h2>
          <button
            onClick={() => setShowAddLog(!showAddLog)}
            data-testid="add-log-btn"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-primary text-white font-body font-medium text-xs hover:bg-primary-hover transition-all"
          >
            <Plus size={14} /> Log Session
          </button>
        </div>

        {showAddLog && (
          <div className="p-4 rounded-2xl bg-background-secondary border border-stone-800 mb-4 space-y-3" data-testid="add-log-form">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-stone-500 text-xs font-body block mb-1">Date</label>
                <input
                  type="date"
                  value={newLog.date}
                  onChange={(e) => setNewLog({...newLog, date: e.target.value})}
                  data-testid="log-date-input"
                  className="w-full px-3 py-2 rounded-xl bg-stone-800 border border-stone-700 text-stone-200 font-body text-sm focus:outline-none focus:border-primary/50"
                />
              </div>
              <div>
                <label className="text-stone-500 text-xs font-body block mb-1">Duration (min)</label>
                <input
                  type="number"
                  value={newLog.duration_minutes}
                  onChange={(e) => setNewLog({...newLog, duration_minutes: Number(e.target.value)})}
                  data-testid="log-duration-input"
                  className="w-full px-3 py-2 rounded-xl bg-stone-800 border border-stone-700 text-stone-200 font-body text-sm focus:outline-none focus:border-primary/50"
                />
              </div>
            </div>
            <div>
              <label className="text-stone-500 text-xs font-body block mb-1">Notes</label>
              <textarea
                value={newLog.notes}
                onChange={(e) => setNewLog({...newLog, notes: e.target.value})}
                placeholder="What did you practice?"
                data-testid="log-notes-input"
                className="w-full px-3 py-2 rounded-xl bg-stone-800 border border-stone-700 text-stone-200 font-body text-sm resize-none h-20 placeholder:text-stone-600 focus:outline-none focus:border-primary/50"
              />
            </div>
            <button
              onClick={addPracticeLog}
              data-testid="save-log-btn"
              className="w-full py-2.5 rounded-xl bg-primary text-white font-body font-medium text-sm hover:bg-primary-hover transition-all"
            >
              Save
            </button>
          </div>
        )}

        {logs.length > 0 ? (
          <div className="space-y-2">
            {logs.map((log) => (
              <div key={log.id} className="flex items-center justify-between p-4 rounded-xl bg-background-secondary border border-stone-800" data-testid={`log-entry-${log.id}`}>
                <div className="flex items-center gap-3">
                  <Clock size={16} className="text-blue-400" />
                  <div>
                    <p className="font-body font-medium text-stone-200 text-sm">{log.date} &middot; {log.duration_minutes} min</p>
                    {log.notes && <p className="text-stone-500 text-xs mt-0.5">{log.notes}</p>}
                  </div>
                </div>
                <button onClick={() => removeLog(log.id)} data-testid={`delete-log-${log.id}`} className="p-2 text-stone-600 hover:text-red-400 transition-colors">
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-stone-600 text-sm font-body py-4">No practice sessions logged yet. Start logging!</p>
        )}
      </section>
    </div>
  );
}
