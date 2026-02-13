import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Trash2, BookOpen, FileText, Music2, ExternalLink } from 'lucide-react';
import { api } from '../utils/api';

const typeConfig = {
  lesson: { icon: BookOpen, color: 'text-amber-400', path: '/lessons' },
  sheet_music: { icon: FileText, color: 'text-purple-400', path: '/sheet-music' },
  theory: { icon: Music2, color: 'text-emerald-400', path: '/theory' },
};

export default function Bookmarks() {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getBookmarks().then(setBookmarks).catch(console.error).finally(() => setLoading(false));
  }, []);

  const removeBookmark = async (id) => {
    await api.removeBookmark(id);
    setBookmarks(bookmarks.filter(b => b.id !== id));
  };

  return (
    <div className="space-y-8" data-testid="bookmarks-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-stone-100">Bookmarks</h1>
        <p className="text-stone-400 font-body text-sm mt-2">Your saved lessons, theory topics, and sheet music</p>
      </div>

      {loading ? (
        <div className="text-stone-500 text-center py-12">Loading...</div>
      ) : bookmarks.length > 0 ? (
        <div className="space-y-2" data-testid="bookmarks-list">
          {bookmarks.map((bm) => {
            const config = typeConfig[bm.item_type] || typeConfig.lesson;
            const Icon = config.icon;
            return (
              <div key={bm.id} className="flex items-center gap-4 p-4 rounded-xl bg-background-secondary border border-stone-800" data-testid={`bookmark-${bm.id}`}>
                <div className={`w-9 h-9 rounded-lg bg-stone-800 flex items-center justify-center ${config.color} shrink-0`}>
                  <Icon size={16} strokeWidth={1.5} />
                </div>
                <div className="flex-1 min-w-0">
                  <Link
                    to={`${config.path}/${bm.item_id}`}
                    className="font-body font-medium text-stone-200 text-sm hover:text-primary transition-colors truncate block"
                    data-testid={`bookmark-link-${bm.id}`}
                  >
                    {bm.title}
                  </Link>
                  <p className="text-stone-600 text-[10px] capitalize mt-0.5">{bm.item_type.replace('_', ' ')}</p>
                </div>
                <Link to={`${config.path}/${bm.item_id}`} className="p-2 text-stone-600 hover:text-primary transition-colors" data-testid={`bookmark-open-${bm.id}`}>
                  <ExternalLink size={14} />
                </Link>
                <button onClick={() => removeBookmark(bm.id)} data-testid={`bookmark-delete-${bm.id}`} className="p-2 text-stone-600 hover:text-red-400 transition-colors">
                  <Trash2 size={14} />
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16" data-testid="bookmarks-empty">
          <FileText size={40} className="text-stone-700 mx-auto mb-4" />
          <p className="text-stone-500 font-body text-sm">No bookmarks yet</p>
          <p className="text-stone-600 font-body text-xs mt-1">Bookmark lessons, theory topics, and sheet music for quick access</p>
        </div>
      )}
    </div>
  );
}
