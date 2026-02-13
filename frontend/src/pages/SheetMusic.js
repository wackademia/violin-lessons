import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Search, Filter } from 'lucide-react';
import { api } from '../utils/api';

const diffColors = {
  beginner: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  intermediate: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  advanced: 'bg-red-500/10 text-red-400 border-red-500/20',
};

export default function SheetMusic() {
  const [pieces, setPieces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [diffFilter, setDiffFilter] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.getSheetMusic().then(setPieces).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = pieces.filter(p => {
    const matchDiff = diffFilter === 'all' || p.difficulty === diffFilter;
    const matchSearch = !search || p.title.toLowerCase().includes(search.toLowerCase()) || p.composer.toLowerCase().includes(search.toLowerCase());
    return matchDiff && matchSearch;
  });

  return (
    <div className="space-y-8" data-testid="sheet-music-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-stone-100">Sheet Music Library</h1>
        <p className="text-stone-400 font-body text-sm mt-2">Public domain classical works for violin</p>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or composer..."
            data-testid="sheet-music-search"
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-background-secondary border border-stone-700 text-stone-200 font-body text-sm placeholder:text-stone-600 focus:outline-none focus:border-primary/50"
          />
        </div>
        <div className="flex gap-2" data-testid="sheet-music-filters">
          {['all', 'beginner', 'intermediate', 'advanced'].map((d) => (
            <button
              key={d}
              onClick={() => setDiffFilter(d)}
              data-testid={`filter-${d}`}
              className={`px-3 py-2 rounded-xl text-xs font-body font-medium capitalize transition-all ${
                diffFilter === d ? 'bg-primary text-white' : 'bg-stone-800 text-stone-400 hover:text-stone-200'
              }`}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-stone-500 text-center py-12">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="sheet-music-list">
          {filtered.map((piece) => (
            <Link
              key={piece.id}
              to={`/sheet-music/${piece.id}`}
              data-testid={`piece-card-${piece.id}`}
              className="group p-5 rounded-2xl bg-background-secondary border border-stone-800 hover:border-primary/30 transition-all duration-300"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="font-body font-semibold text-stone-200 text-sm group-hover:text-primary transition-colors">{piece.title}</h3>
                  <p className="text-stone-500 text-xs mt-0.5">{piece.composer}</p>
                </div>
                <ChevronRight size={16} className="text-stone-600 group-hover:text-primary transition-colors shrink-0 mt-1" />
              </div>
              <p className="text-stone-500 text-xs mt-2 line-clamp-2">{piece.description}</p>
              <div className="flex items-center gap-2 mt-3">
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border ${diffColors[piece.difficulty]}`}>
                  {piece.difficulty}
                </span>
                <span className="text-stone-600 text-[10px]">{piece.key}</span>
                <span className="text-stone-600 text-[10px]">{piece.time_signature}</span>
              </div>
            </Link>
          ))}
          {filtered.length === 0 && (
            <div className="col-span-2 text-stone-500 text-center py-12">No pieces found matching your filters.</div>
          )}
        </div>
      )}
    </div>
  );
}
