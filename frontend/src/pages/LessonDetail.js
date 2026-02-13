import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, Bookmark, BookmarkCheck, Lightbulb, Play, Dumbbell } from 'lucide-react';
import { api } from '../utils/api';

export default function LessonDetail() {
  const { id } = useParams();
  const [lesson, setLesson] = useState(null);
  const [progress, setProgress] = useState(null);
  const [bookmarked, setBookmarked] = useState(false);
  const [bookmarkId, setBookmarkId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getLesson(id), api.getProgress(), api.getBookmarks()])
      .then(([l, prog, bm]) => {
        setLesson(l);
        const p = prog.find(x => x.item_id === id && x.item_type === 'lesson');
        setProgress(p || null);
        const b = bm.find(x => x.item_id === id && x.item_type === 'lesson');
        if (b) { setBookmarked(true); setBookmarkId(b.id); }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  const toggleComplete = async () => {
    const completed = !progress?.completed;
    const result = await api.updateProgress({ item_id: id, item_type: 'lesson', completed });
    setProgress(result);
  };

  const toggleBookmark = async () => {
    if (bookmarked) {
      await api.removeBookmark(bookmarkId);
      setBookmarked(false);
      setBookmarkId(null);
    } else {
      const bm = await api.addBookmark({ item_id: id, item_type: 'lesson', title: lesson.title });
      setBookmarked(true);
      setBookmarkId(bm.id);
    }
  };

  if (loading) return <div className="text-stone-500 text-center py-12">Loading...</div>;
  if (!lesson) return <div className="text-stone-500 text-center py-12">Lesson not found</div>;

  return (
    <div className="space-y-8" data-testid="lesson-detail-page">
      <Link to="/lessons" className="inline-flex items-center gap-2 text-stone-400 hover:text-primary text-sm font-body transition-colors" data-testid="back-to-lessons">
        <ArrowLeft size={16} /> Back to Lessons
      </Link>

      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-2xl md:text-3xl font-bold text-stone-100" data-testid="lesson-title">{lesson.title}</h1>
          <p className="text-stone-400 font-body text-sm mt-2">{lesson.description}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={toggleBookmark}
            data-testid="bookmark-btn"
            className="p-2.5 rounded-xl border border-stone-700 hover:border-primary/30 transition-colors"
          >
            {bookmarked ? <BookmarkCheck size={18} className="text-primary" /> : <Bookmark size={18} className="text-stone-400" />}
          </button>
          <button
            onClick={toggleComplete}
            data-testid="complete-btn"
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full font-body font-medium text-sm transition-all ${
              progress?.completed
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-primary text-white hover:bg-primary-hover'
            }`}
          >
            <CheckCircle2 size={16} />
            {progress?.completed ? 'Completed' : 'Mark Complete'}
          </button>
        </div>
      </div>

      {/* YouTube Video */}
      {lesson.youtube_id && (
        <div className="rounded-2xl overflow-hidden border border-stone-800 aspect-video" data-testid="lesson-video">
          <iframe
            src={`https://www.youtube.com/embed/${lesson.youtube_id}`}
            title={lesson.title}
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      )}

      {/* Content */}
      <div className="space-y-4" data-testid="lesson-content">
        {lesson.content?.map((block, idx) => (
          <ContentBlock key={idx} block={block} />
        ))}
      </div>
    </div>
  );
}

function ContentBlock({ block }) {
  switch (block.type) {
    case 'heading':
      return <h2 className="font-heading text-xl font-bold text-stone-100 mt-6 mb-2">{block.value}</h2>;
    case 'text':
      return <p className="text-stone-300 font-body text-sm leading-relaxed">{block.value}</p>;
    case 'tip':
      return (
        <div className="flex gap-3 p-4 rounded-xl bg-amber-500/5 border border-amber-500/20" data-testid="lesson-tip">
          <Lightbulb size={18} className="text-amber-400 shrink-0 mt-0.5" />
          <p className="text-amber-200/80 font-body text-sm leading-relaxed">{block.value}</p>
        </div>
      );
    case 'exercise':
      return (
        <div className="flex gap-3 p-4 rounded-xl bg-blue-500/5 border border-blue-500/20" data-testid="lesson-exercise">
          <Dumbbell size={18} className="text-blue-400 shrink-0 mt-0.5" />
          <p className="text-blue-200/80 font-body text-sm leading-relaxed">{block.value}</p>
        </div>
      );
    default:
      return <p className="text-stone-300 font-body text-sm">{block.value}</p>;
  }
}
