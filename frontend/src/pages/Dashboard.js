import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Music, Activity, FileText, Wrench, Calendar, ChevronRight, Flame, Clock, Trophy } from 'lucide-react';
import { api } from '../utils/api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  const quickLinks = [
    { path: '/lessons', label: 'Lessons', icon: BookOpen, desc: 'Progressive violin courses', color: 'text-amber-400' },
    { path: '/theory', label: 'Music Theory', icon: Music, desc: 'Notation, rhythm & keys', color: 'text-emerald-400' },
    { path: '/tuner', label: 'Violin Tuner', icon: Activity, desc: 'Tune your instrument', color: 'text-blue-400' },
    { path: '/sheet-music', label: 'Sheet Music', icon: FileText, desc: 'Classical library', color: 'text-purple-400' },
    { path: '/care', label: 'Care & Maintenance', icon: Wrench, desc: 'Keep your violin perfect', color: 'text-rose-400' },
    { path: '/practice', label: 'Practice Scheduler', icon: Calendar, desc: 'Plan your sessions', color: 'text-cyan-400' },
  ];

  return (
    <div className="space-y-10" data-testid="dashboard-page">
      {/* Hero */}
      <section className="relative rounded-3xl overflow-hidden" data-testid="dashboard-hero">
        <div className="absolute inset-0 bg-gradient-to-br from-stone-900/95 via-stone-900/80 to-stone-800/70 z-10" />
        <img
          src="https://images.unsplash.com/photo-1577923873566-c65cea4b859f?w=1200&q=80"
          alt="Violin close-up"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="relative z-20 px-6 md:px-12 py-12 md:py-20">
          <h1 className="font-heading text-3xl md:text-5xl font-bold text-stone-100 tracking-tight leading-tight" data-testid="hero-title">
            Master the Violin,<br />
            <span className="text-primary">One Note at a Time</span>
          </h1>
          <p className="mt-4 text-stone-400 font-body text-sm md:text-base max-w-lg leading-relaxed">
            Your free, comprehensive journey from beginner to virtuoso. Interactive lessons, music theory, a built-in tuner, and a classical sheet music library.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/lessons"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-primary text-white font-body font-semibold text-sm hover:bg-primary-hover transition-all hover:scale-105 active:scale-95 shadow-lg shadow-primary/20"
              data-testid="start-learning-btn"
            >
              Start Learning <ChevronRight size={16} />
            </Link>
            <Link
              to="/tuner"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-stone-600 text-stone-300 font-body font-medium text-sm hover:bg-stone-800 transition-all"
              data-testid="open-tuner-btn"
            >
              <Activity size={16} /> Open Tuner
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      {stats && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4" data-testid="stats-section">
          <StatCard icon={<Flame size={20} className="text-orange-400" />} value={stats.practice_streak} label="Day Streak" testId="stat-streak" />
          <StatCard icon={<Clock size={20} className="text-blue-400" />} value={stats.total_practice_minutes} label="Minutes Practiced" testId="stat-minutes" />
          <StatCard icon={<Trophy size={20} className="text-amber-400" />} value={`${stats.completed_lessons}/${stats.total_lessons}`} label="Lessons Done" testId="stat-lessons" />
          <StatCard icon={<FileText size={20} className="text-purple-400" />} value={stats.total_sheet_music} label="Sheet Music Pieces" testId="stat-pieces" />
        </section>
      )}

      {/* Quick Links */}
      <section data-testid="quick-links-section">
        <h2 className="font-heading text-2xl font-bold text-stone-100 mb-6">Explore</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              data-testid={`quick-link-${link.label.toLowerCase().replace(/\s+/g, '-')}`}
              className="group flex items-center gap-4 p-5 rounded-2xl bg-background-secondary border border-stone-800 hover:border-primary/30 transition-all duration-300 hover:shadow-xl hover:-translate-y-0.5"
            >
              <div className={`w-12 h-12 rounded-xl bg-stone-800 flex items-center justify-center ${link.color} group-hover:scale-110 transition-transform`}>
                <link.icon size={22} strokeWidth={1.5} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-body font-semibold text-stone-200 text-sm">{link.label}</h3>
                <p className="text-stone-500 text-xs mt-0.5">{link.desc}</p>
              </div>
              <ChevronRight size={16} className="text-stone-600 group-hover:text-primary transition-colors" />
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

function StatCard({ icon, value, label, testId }) {
  return (
    <div className="p-4 md:p-5 rounded-2xl bg-background-secondary border border-stone-800" data-testid={testId}>
      <div className="flex items-center gap-2 mb-2">{icon}</div>
      <p className="font-heading text-2xl md:text-3xl font-bold text-stone-100">{value}</p>
      <p className="text-stone-500 text-xs font-body mt-1">{label}</p>
    </div>
  );
}
