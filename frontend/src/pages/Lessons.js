import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, CheckCircle2, Clock, Music } from 'lucide-react';
import { api } from '../utils/api';

const levelColors = {
  beginner: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  intermediate: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  advanced: 'bg-red-500/10 text-red-400 border-red-500/20',
};

const categoryLabels = {
  fundamentals: 'Fundamentals',
  bowing: 'Bowing',
  finger_positioning: 'Finger Positioning',
  repertoire: 'Repertoire',
  technique: 'Technique',
};

export default function Lessons() {
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getLessons(), api.getProgress()])
      .then(([l, p]) => { setLessons(l); setProgress(p); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const isCompleted = (lessonId) => progress.some(p => p.item_id === lessonId && p.item_type === 'lesson' && p.completed);

  const filtered = filter === 'all' ? lessons : lessons.filter(l => l.level === filter);

  return (
    <div className="space-y-8" data-testid="lessons-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-stone-100">Violin Lessons</h1>
        <p className="text-stone-400 font-body text-sm mt-2">Progressive lessons from beginner to advanced</p>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap" data-testid="lesson-filters">
        {['all', 'beginner', 'intermediate', 'advanced'].map((level) => (
          <button
            key={level}
            onClick={() => setFilter(level)}
            data-testid={`filter-${level}`}
            className={`px-4 py-2 rounded-full text-xs font-body font-medium capitalize transition-all ${
              filter === level
                ? 'bg-primary text-white'
                : 'bg-stone-800 text-stone-400 hover:text-stone-200'
            }`}
          >
            {level}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-stone-500 text-center py-12">Loading lessons...</div>
      ) : (
        <div className="space-y-3" data-testid="lessons-list">
          {filtered.map((lesson, idx) => (
            <Link
              key={lesson.id}
              to={`/lessons/${lesson.id}`}
              data-testid={`lesson-card-${lesson.id}`}
              className="group flex items-center gap-4 p-4 md:p-5 rounded-2xl bg-background-secondary border border-stone-800 hover:border-primary/30 transition-all duration-300"
            >
              <div className="w-10 h-10 rounded-xl bg-stone-800 flex items-center justify-center text-stone-400 font-heading font-bold text-sm shrink-0">
                {isCompleted(lesson.id) ? (
                  <CheckCircle2 size={20} className="text-emerald-400" />
                ) : (
                  <span>{lesson.order}</span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-body font-semibold text-stone-200 text-sm group-hover:text-primary transition-colors truncate">{lesson.title}</h3>
                <p className="text-stone-500 text-xs mt-0.5 truncate">{lesson.description}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border ${levelColors[lesson.level]}`}>
                    {lesson.level}
                  </span>
                  <span className="text-stone-600 text-[10px] flex items-center gap-1">
                    <Clock size={10} /> {lesson.duration_minutes} min
                  </span>
                  <span className="text-stone-600 text-[10px] flex items-center gap-1">
                    <Music size={10} /> {categoryLabels[lesson.category] || lesson.category}
                  </span>
                </div>
              </div>
              <ChevronRight size={16} className="text-stone-600 group-hover:text-primary transition-colors shrink-0" />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
