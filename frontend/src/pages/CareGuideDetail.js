import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Lightbulb, CheckCircle } from 'lucide-react';
import { api } from '../utils/api';

export default function CareGuideDetail() {
  const { id } = useParams();
  const [guide, setGuide] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCareGuide(id).then(setGuide).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-stone-500 text-center py-12">Loading...</div>;
  if (!guide) return <div className="text-stone-500 text-center py-12">Guide not found</div>;

  return (
    <div className="space-y-8" data-testid="care-guide-detail-page">
      <Link to="/care" className="inline-flex items-center gap-2 text-stone-400 hover:text-primary text-sm font-body transition-colors" data-testid="back-to-care">
        <ArrowLeft size={16} /> Back to Care Guides
      </Link>

      <div>
        <h1 className="font-heading text-2xl md:text-3xl font-bold text-stone-100" data-testid="care-title">{guide.title}</h1>
        <p className="text-stone-400 font-body text-sm mt-2">{guide.description}</p>
      </div>

      <div className="space-y-4" data-testid="care-content">
        {guide.content?.map((block, idx) => {
          switch (block.type) {
            case 'text':
              return <p key={idx} className="text-stone-300 font-body text-sm leading-relaxed">{block.value}</p>;
            case 'step':
              return (
                <div key={idx} className="flex gap-3 p-3 rounded-xl bg-stone-800/30">
                  <CheckCircle size={16} className="text-emerald-400 shrink-0 mt-0.5" />
                  <p className="text-stone-300 font-body text-sm">{block.value}</p>
                </div>
              );
            case 'warning':
              return (
                <div key={idx} className="flex gap-3 p-4 rounded-xl bg-red-500/5 border border-red-500/20">
                  <AlertTriangle size={18} className="text-red-400 shrink-0 mt-0.5" />
                  <p className="text-red-200/80 font-body text-sm leading-relaxed">{block.value}</p>
                </div>
              );
            case 'tip':
              return (
                <div key={idx} className="flex gap-3 p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
                  <Lightbulb size={18} className="text-amber-400 shrink-0 mt-0.5" />
                  <p className="text-amber-200/80 font-body text-sm leading-relaxed">{block.value}</p>
                </div>
              );
            default:
              return <p key={idx} className="text-stone-300 font-body text-sm">{block.value}</p>;
          }
        })}
      </div>
    </div>
  );
}
