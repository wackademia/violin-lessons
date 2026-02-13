import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Bookmark, BookmarkCheck, Music } from 'lucide-react';
import { api } from '../utils/api';

export default function SheetMusicDetail() {
  const { id } = useParams();
  const [piece, setPiece] = useState(null);
  const [bookmarked, setBookmarked] = useState(false);
  const [bookmarkId, setBookmarkId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getSheetMusicPiece(id), api.getBookmarks()])
      .then(([p, bm]) => {
        setPiece(p);
        const b = bm.find(x => x.item_id === id && x.item_type === 'sheet_music');
        if (b) { setBookmarked(true); setBookmarkId(b.id); }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  const toggleBookmark = async () => {
    if (bookmarked) {
      await api.removeBookmark(bookmarkId);
      setBookmarked(false);
      setBookmarkId(null);
    } else {
      const bm = await api.addBookmark({ item_id: id, item_type: 'sheet_music', title: piece.title });
      setBookmarked(true);
      setBookmarkId(bm.id);
    }
  };

  if (loading) return <div className="text-stone-500 text-center py-12">Loading...</div>;
  if (!piece) return <div className="text-stone-500 text-center py-12">Piece not found</div>;

  const diffColor = {
    beginner: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    intermediate: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    advanced: 'bg-red-500/10 text-red-400 border-red-500/20',
  };

  return (
    <div className="space-y-8" data-testid="sheet-music-detail-page">
      <Link to="/sheet-music" className="inline-flex items-center gap-2 text-stone-400 hover:text-primary text-sm font-body transition-colors" data-testid="back-to-library">
        <ArrowLeft size={16} /> Back to Library
      </Link>

      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl md:text-3xl font-bold text-stone-100" data-testid="piece-title">{piece.title}</h1>
          <p className="text-stone-400 font-body text-base mt-1" data-testid="piece-composer">{piece.composer}</p>
          <div className="flex items-center gap-2 mt-3">
            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${diffColor[piece.difficulty]}`}>
              {piece.difficulty}
            </span>
            <span className="text-stone-500 text-xs">Key: {piece.key}</span>
            <span className="text-stone-500 text-xs">Time: {piece.time_signature}</span>
          </div>
        </div>
        <button onClick={toggleBookmark} data-testid="bookmark-btn" className="p-2.5 rounded-xl border border-stone-700 hover:border-primary/30 transition-colors shrink-0">
          {bookmarked ? <BookmarkCheck size={18} className="text-primary" /> : <Bookmark size={18} className="text-stone-400" />}
        </button>
      </div>

      <div className="p-6 rounded-2xl bg-background-secondary border border-stone-800" data-testid="piece-description">
        <p className="text-stone-300 font-body text-sm leading-relaxed">{piece.description}</p>
      </div>

      {/* Visual Notation Display */}
      <div className="rounded-2xl bg-stone-100 p-6 md:p-8" data-testid="notation-display">
        <div className="flex items-center gap-3 mb-4">
          <Music size={20} className="text-stone-700" />
          <h3 className="font-heading text-lg font-bold text-stone-900">{piece.title}</h3>
        </div>
        <div className="font-mono text-base md:text-lg text-stone-800 tracking-wider leading-loose border-t border-stone-300 pt-4">
          {piece.notes}
        </div>
        <p className="text-stone-500 text-xs mt-4 font-body">{piece.key} &middot; {piece.time_signature}</p>
      </div>

      <div className="p-4 rounded-xl bg-stone-800/30 border border-stone-700/50">
        <p className="text-stone-500 text-xs font-body leading-relaxed" data-testid="piece-attribution">
          Attribution: {piece.attribution}
        </p>
      </div>
    </div>
  );
}
