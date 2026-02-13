import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Music2, Drum, Key, Hash, Sparkles } from 'lucide-react';
import { api } from '../utils/api';

const catIcons = {
  notation: Music2,
  rhythm: Drum,
  keys: Key,
  expression: Sparkles,
  ear_training: Hash,
};

const catColors = {
  notation: 'text-violet-400',
  rhythm: 'text-amber-400',
  keys: 'text-emerald-400',
  expression: 'text-rose-400',
  ear_training: 'text-blue-400',
};

export default function Theory() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTheory().then(setTopics).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8" data-testid="theory-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-stone-100">Music Theory</h1>
        <p className="text-stone-400 font-body text-sm mt-2">Essential theory for violin players</p>
      </div>

      {loading ? (
        <div className="text-stone-500 text-center py-12">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="theory-list">
          {topics.map((topic) => {
            const Icon = catIcons[topic.category] || Music2;
            const color = catColors[topic.category] || 'text-stone-400';
            return (
              <Link
                key={topic.id}
                to={`/theory/${topic.id}`}
                data-testid={`theory-card-${topic.id}`}
                className="group flex items-start gap-4 p-5 rounded-2xl bg-background-secondary border border-stone-800 hover:border-primary/30 transition-all duration-300"
              >
                <div className={`w-11 h-11 rounded-xl bg-stone-800 flex items-center justify-center ${color} shrink-0`}>
                  <Icon size={20} strokeWidth={1.5} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-body font-semibold text-stone-200 text-sm group-hover:text-primary transition-colors">{topic.title}</h3>
                  <p className="text-stone-500 text-xs mt-1 line-clamp-2">{topic.description}</p>
                  <span className="inline-block mt-2 text-[10px] text-stone-600 capitalize">{topic.category?.replace('_', ' ')}</span>
                </div>
                <ChevronRight size={16} className="text-stone-600 group-hover:text-primary transition-colors mt-1 shrink-0" />
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
